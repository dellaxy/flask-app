import secrets, bcrypt
from flask import Flask, redirect, render_template, jsonify, request, session
from flask_paginate import Pagination, get_page_parameter
from bson import ObjectId
from flask_pymongo import pymongo

CONNECTION_STRING = "mongodb+srv://bernath:Password123@ukf.fwchxj9.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database("blog")

article_collection = pymongo.collection.Collection(db, "articles")
category_collection = pymongo.collection.Collection(db, "categories")
user_collection = pymongo.collection.Collection(db, "users")

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

secret_key = secrets.token_hex(16)
app.secret_key = secret_key

# Login / Registration ----------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        loginUsername = request.form.get("username")
        loginPassword = request.form.get("password")
        dbUser = user_collection.find_one({"username": loginUsername})
        if dbUser is None:
            return render_template(
                "login.html",
                error_message="User does not exist. Please try again or create new account.",
            )
        else:
            return userValidation(loginUsername, loginPassword, dbUser)

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

def userValidation(username, password, dbUser):
    if username == dbUser["username"] and bcrypt.checkpw(
        password.encode("utf-8"), dbUser["password"]
    ):
        session["logged_in"] = True
        session["user_id"] = str(dbUser["_id"])
        session["is_admin"] = True if dbUser["admin"] else False
        return redirect("/")
    else:
        return render_template(
            "login.html",
            error_message="Invalid username or password. Please try again.",
        )

@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        username = request.form.get("username")
        if(user_collection.find_one({"username": username})):
            return render_template(
                "registration.html",
                error_message="User with this username already exists. Please try again.",
            )
        else:
            name = request.form.get("name")
            surname = request.form.get("surname")
            password = request.form.get("password")
            user = {
                "_id": ObjectId(),
                "username": username,
                "password": bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()),
                "name": name,
                "surname": surname,
                "admin": False,
            }
            user_collection.insert_one(user)
            return redirect("/login")
    return render_template("registration.html")

# Home page / Admin -------------------------------------------------------------------------------------

@app.route("/")
def home():
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 6
    total = article_collection.count_documents({})

    articles = get_articles(page=page, per_page=per_page, categoryId=None)

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework="bootstrap5")

    if session.get("is_admin"):
        return render_template("admin.html", articles=articles, pagination=pagination)
    return render_template("index.html", articles=articles, pagination=pagination, logged_in=session.get("logged_in"))


def get_articles(page, per_page, categoryId):
    articles = []
    start_index = (page - 1) * per_page
    end_index = start_index + per_page
    if categoryId:
        for article in article_collection.find({"category_id" : ObjectId(categoryId)}).skip(start_index).limit(per_page):
            article["category"] = category_collection.find_one({"_id": article["category_id"]}).get("category")
            articles.append(article)
    else:
        for article in article_collection.find().skip(start_index).limit(per_page):
            article["category"] = category_collection.find_one({"_id": article["category_id"]}).get("category")
            articles.append(article)

    return articles

# Articles -----------------------------------------------------------------------------------------------

@app.route("/articles/<article_id>")
def show_article(article_id):
    article = article_collection.find_one({"_id": ObjectId(article_id)})
    article["category"] = category_collection.find_one({"_id": article["category_id"]}).get("category")
    return render_template("article.html", article=article, logged_in=session.get("logged_in"), pagination=None)


@app.route("/article/<article_id>", methods=["POST"])
def update_article(article_id):
    title = request.form.get("title")
    content = request.form.get("content")
    lead = request.form.get("lead-paragraph")
    category_id = request.form.get("category")
    article = {
        "title": title,
        "content": content,
        "lead_paragraph": lead,
        "category_id": ObjectId(category_id),
    }
    article_collection.update_one({"_id": ObjectId(article_id)}, {"$set": article})
    return redirect("/")


@app.route("/article", methods=["POST"])
def create_article():
    title = request.form.get("title")
    content = request.form.get("content")
    lead = request.form.get("lead-paragraph")
    category_id = request.form.get("category")
    article = {
        "_id": ObjectId(),
        "title": title,
        "content": content,
        "lead_paragraph": lead,
        "category_id": ObjectId(category_id),
    }
    article_collection.insert_one(article)
    return redirect("/")


@app.route("/article/<article_id>", methods=["GET"])
def get_article(article_id):
    article = article_collection.find_one({"_id": ObjectId(article_id)})
    article["_id"] = str(article.get("_id"))
    article["category_id"] = str(article.get("category_id"))
    article["category"] = category_collection.find_one(
        {"_id": ObjectId(article["category_id"])}
    ).get("category")
    return jsonify(article)


@app.route("/article/<article_id>", methods=["DELETE"])
def delete_article(article_id):
    result = article_collection.delete_one({"_id": ObjectId(article_id)})
    if result.deleted_count == 1:
        return jsonify({"success": True})
# Categories ---------------------------------------------------------------------------------------------

@app.route("/categories")
def categories():
    categories = []
    for category in category_collection.find():
        category["_id"] = str(category.get("_id"))
        categories.append(category)
    return jsonify(categories)


@app.route("/category/<category_id>", methods=["GET"])
def find_category(category_id):
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 6
    total = article_collection.count_documents({"category_id": ObjectId(category_id)})

    articles = get_articles(page=page, per_page=per_page, categoryId=category_id)

    pagination = Pagination(page=page, total=total, per_page=per_page, css_framework="bootstrap5")

    return render_template("index.html", articles=articles, category_name = category_collection.find_one({"_id": ObjectId(category_id)}).get("category"), pagination=pagination)


@app.route("/category", methods=["POST"])
def create_category():
    category = {
        "_id": ObjectId(),
        "category": request.form.get("category-name"),
    }
    category_collection.insert_one(category)
    return redirect("/")


@app.route("/category/<category_id>", methods=["DELETE"])
def delete_category(category_id):
    articles_with_category = article_collection.count_documents({"category_id": ObjectId(category_id)})
    if articles_with_category > 0:
        return "", 400
    else:
        category_collection.delete_one({"_id": ObjectId(category_id)})
        return "", 200


@app.route("/category/<category_id>", methods=["POST"])
def update_category(category_id):
    category = {
        "category": request.form.get("category-name")
    }
    category_collection.update_one({"_id": ObjectId(category_id)}, {"$set": category})
    return redirect("/")

# Users ------------------------------------------------------------------------------------------------

@app.route("/users", methods=["GET"])
def get_users():
    users = []
    for user in user_collection.find({}, {"password": 0}):
        user["_id"] = str(user.get("_id"))
        users.append(user)
    return jsonify(users)


# Charts ------------------------------------------------------------------------------------------------

@app.route('/chartdata')
def chartdata():
    categories = category_collection.find()
    data = []

    for category in categories:
        category_id = category.get("_id")
        category_count = article_collection.count_documents({'category_id': ObjectId(category_id)})
        data.append({'category': category.get("category"), 'count': category_count})

    return jsonify(data)

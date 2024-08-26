"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
from flask import Flask, request, jsonify, url_for, Blueprint
from flask_jwt_extended import create_access_token, get_jwt_identity, get_jwt, jwt_required
from api.models import db, User, TokenBlockedList
from api.utils import generate_sitemap, APIException
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from tempfile import NamedTemporaryFile
from firebase_admin import storage
from datetime import timedelta
import os
import requests
import json


app = Flask(__name__)
bcrypt = Bcrypt(app)

api = Blueprint('api', __name__)

# Allow CORS requests to this API
CORS(api)


@api.route('/signup', methods=['POST'])
def user_signup():
    body = request.get_json()

    if "email" not in body:
        return jsonify({"msg": "El campo email es requerido"}), 400
    if "password" not in body:
        return jsonify({"msg": "El campo password es requerido"}), 400

    encrypted_password = bcrypt.generate_password_hash(
        body["password"]).decode('utf-8')

    new_user = User(email=body["email"],
                    password=encrypted_password, is_active=True)

    if "first_name" in body:
        new_user.first_name = body["first_name"]
    else:
        new_user.first_name = ""

    if "last_name" in body:
        new_user.last_name = body["last_name"]
    else:
        new_user.last_name = ""

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "ok"})


@api.route('/login', methods=['POST'])
def user_login():
    body = request.get_json()
    # 1. Valido los campos del body de la peticion
    if "email" not in body:
        return jsonify({"msg": "El campo email es requerido"}), 400
    if "password" not in body:
        return jsonify({"msg": "El campo password es requerido"}), 400

    # 2. Busco al usuario en la base de datos con el correo
    user = User.query.filter_by(email=body["email"]).first()

    # 2.1 Si el usuario no aparece, retorna un error 404
    if user is None:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    # 3 Verifico el campo password del body con el password del usuario de la base de datos
    password_checked = bcrypt.check_password_hash(
        user.password, body["password"])
    # 3.1 Si no se verifica se retorna un error de clave inválida 401
    if password_checked == False:
        return jsonify({"msg": "Clave invalida"}), 401

    # 4 Generar el token
    role = "admin"
    if user.id % 2 == 0:
        role = "user"
    token = create_access_token(
        identity=user.id, additional_claims={"role": role})
    output = {"token": token,
              "profilePicture": user.getProfilePicture()}

    return jsonify(output), 200


@api.route('/logout', methods=['POST'])
@jwt_required()
def user_logout():
    jti = get_jwt()["jti"]
    token_blocked = TokenBlockedList(jti=jti)
    db.session.add(token_blocked)
    db.session.commit()
    return jsonify({"msg": "Sesion cerrada"})


@api.route("/userinfo", methods=['GET'])
@jwt_required()
def user_info():
    user = User.query.filter_by(id=get_jwt_identity()).first()
    if user is None:
        return jsonify({"msg": "User not foud"}), 404
    payload = get_jwt()
    return jsonify({"user": user.id, "role": payload["role"], "profilePicture": user.getProfilePicture()})


@api.route("/profilepic", methods=["PUT"])
@jwt_required()
def user_picture():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"msg": "User not found"}), 404
    # Recibo el archivo
    file = request.files["profilePic"]
    extension = file.filename.split(".")[1]
    # Guardo el archivo de la peticion en un archivo temporal
    temp = NamedTemporaryFile(delete=False)
    file.save(temp.name)
    # Subir el archivo a Firebase
    bucket = storage.bucket()
    filename = "usersPictures/" + str(user_id) + "." + extension
    resource = bucket.blob(filename)
    resource.upload_from_filename(temp.name, content_type="image/" + extension)
    user.profile_pic = filename
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Picture updated", "profilePicture": user.getProfilePicture()})


@api.route("/userinfoadmin", methods=['GET'])
@jwt_required()
def user_info_admin():
    payload = get_jwt()
    if payload["role"] != "admin":
        return jsonify({"msg": "Acceso denegado"}), 401

    user = get_jwt_identity()
    payload = get_jwt()
    return jsonify({"user": user, "role": payload["role"]})


@api.route("/changepassword", methods=['PATCH'])
@jwt_required()
def user_change_password():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    # 2.1 Si el usuario no aparece, retorna un error 404
    if user is None:
        return jsonify({"msg": "Usuario no encontrado"}), 404

    body = request.get_json()
    new_password = bcrypt.generate_password_hash(
        body["password"]).decode('utf-8')
    user.password = new_password
    db.session.add(user)

    if get_jwt()["type"] == "password":
        jti = get_jwt()["jti"]
        token_blocked = TokenBlockedList(jti=jti)
        db.session.flush()
        db.session.add(token_blocked)

    db.session.commit()
    return jsonify({"msg": "Clave actualizada"})


@api.route("/requestpasswordrecovery", methods=['POST'])
def request_password_recovery():
    email = request.get_json()['email']
    user = User.query.filter_by(email=email).first()
    if user is None:
        return jsonify({"msg": "Usuario no encontrado"}), 404
    password_token = create_access_token(
        identity=user.id, additional_claims={"type": "password"})
    url = os.getenv("FRONTEND_URL")

    # Ejemplo: https://curly-succotash-jjvvj79gvxxfqv64-3000.app.github.dev/changepassword?token=31251276357612356712321
    url = url+"/changepassword?token=" + password_token

    # ______________________________
    # ENVIO DE CORREO
    # ______________________________
    send_mail_url = os.getenv("MAIL_SEND_URL")
    private_key = os.getenv("MAIL_PRIVATE_KEY")
    service_id = os.getenv("MAIL_SERVICE_ID")
    template_id = os.getenv("MAIL_TEMPLATE_ID")
    user_id = os.getenv("MAIL_USER_ID")
    data = {
        "service_id": service_id,
        "template_id": template_id,
        "user_id": user_id,
        "accessToken": private_key,
        "template_params": {
            "url": url
        }
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        send_mail_url, headers=headers, data=json.dumps(data))

    print(response.text)
    if response.status_code == 200:
        return jsonify({"msg": "Revise su correo para el cambio de clave "})

    else:
        return jsonify({"msg": "Ocurrio un error con el envio de correo "}), 400

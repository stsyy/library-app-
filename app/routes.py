"""REST API: по 5 CRUD-операций (create, list, get, update, delete) для 5 сущностей = 25 операций."""
from datetime import date

from flask import Blueprint, abort, jsonify, request
from sqlalchemy.exc import IntegrityError

from .models import Author, Book, Genre, Loan, Reader, db

api = Blueprint("api", __name__, url_prefix="/api")


def _parse_date(value):
    return date.fromisoformat(value) if value else None


# Описание полей каждой сущности: имя -> (тип, обязательное, связанная модель)
SCHEMAS = {
    "genres": (Genre, {"name": (str, True, None), "description": (str, False, None)}),
    "authors": (
        Author,
        {"full_name": (str, True, None), "country": (str, False, None), "birth_year": (int, False, None)},
    ),
    "books": (
        Book,
        {
            "title": (str, True, None),
            "year": (int, False, None),
            "copies": (int, False, None),
            "author_id": (int, True, Author),
            "genre_id": (int, False, Genre),
        },
    ),
    "readers": (
        Reader,
        {"full_name": (str, True, None), "email": (str, True, None), "phone": (str, False, None)},
    ),
    "loans": (
        Loan,
        {
            "book_id": (int, True, Book),
            "reader_id": (int, True, Reader),
            "issued_at": (_parse_date, False, None),
            "due_at": (_parse_date, False, None),
            "returned": (bool, False, None),
        },
    ),
}


def _bad_request(message):
    return jsonify({"error": message}), 400


def _apply(obj, fields, data, partial):
    for name, (cast, required, ref_model) in fields.items():
        if name not in data:
            if required and not partial:
                raise ValueError(f"field '{name}' is required")
            continue
        value = data[name]
        if value is None:
            if required:
                raise ValueError(f"field '{name}' cannot be null")
        else:
            try:
                value = cast(value)
            except (TypeError, ValueError):
                raise ValueError(f"field '{name}' has invalid value")
            if ref_model is not None and db.session.get(ref_model, value) is None:
                raise ValueError(f"{ref_model.__name__.lower()} {value} not found")
        setattr(obj, name, value)


def _register(resource, model, fields):
    def list_items():
        return jsonify([o.to_dict() for o in model.query.order_by(model.id).all()])

    def get_item(item_id):
        obj = db.session.get(model, item_id) or abort(404)
        return jsonify(obj.to_dict())

    def create_item():
        obj = model()
        try:
            _apply(obj, fields, request.get_json(silent=True) or {}, partial=False)
            db.session.add(obj)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return _bad_request(str(e))
        except IntegrityError:
            db.session.rollback()
            return _bad_request("integrity error (duplicate value?)")
        return jsonify(obj.to_dict()), 201

    def update_item(item_id):
        obj = db.session.get(model, item_id) or abort(404)
        try:
            _apply(obj, fields, request.get_json(silent=True) or {}, partial=True)
            db.session.commit()
        except ValueError as e:
            db.session.rollback()
            return _bad_request(str(e))
        except IntegrityError:
            db.session.rollback()
            return _bad_request("integrity error (duplicate value?)")
        return jsonify(obj.to_dict())

    def delete_item(item_id):
        obj = db.session.get(model, item_id) or abort(404)
        db.session.delete(obj)
        db.session.commit()
        return "", 204

    api.add_url_rule(f"/{resource}", f"list_{resource}", list_items, methods=["GET"])
    api.add_url_rule(f"/{resource}", f"create_{resource}", create_item, methods=["POST"])
    api.add_url_rule(f"/{resource}/<int:item_id>", f"get_{resource}", get_item, methods=["GET"])
    api.add_url_rule(f"/{resource}/<int:item_id>", f"update_{resource}", update_item, methods=["PUT"])
    api.add_url_rule(f"/{resource}/<int:item_id>", f"delete_{resource}", delete_item, methods=["DELETE"])


for _resource, (_model, _fields) in SCHEMAS.items():
    _register(_resource, _model, _fields)


@api.get("/health")
def health():
    return jsonify({"status": "ok"})

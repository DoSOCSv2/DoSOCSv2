from dosocs2 import schema as db
from pytest import raises

def test_db_create_connection_with_echo():
    engine = db.create_connection('sqlite:///:memory:', echo=True)
    assert engine is not None
    assert engine._echo

def test_db_create_connection_without_echo():
    engine = db.create_connection('sqlite:///:memory:', echo=False)
    assert engine is not None
    assert not engine._echo

def test_db_create_connection_only_one_arg_fails():
    with raises(Exception):
        engine = db.create_connection('sqlite:///:memory:')

def test_db_create_connection_bad_conn_string_fails():
    with raises(Exception):
        engine = db.create_connection('blah', echo=True)

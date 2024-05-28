import pytest

from handy.db import *


pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures('test_table')]


@pytest.fixture
def test_table():
    # NOTE: We wrap that into transaction because in other case django will gobble it up
    #       into single transaction with first test and then rollback everything happily on
    #       that tests end.
    do_sql('''
        begin;

        drop table if exists test;
        create table test (
            id int primary key,
            tag int not null
        );
        insert into test values (1, 10), (2, 20);

        commit;
    ''')


def test_fetch_val():
    assert fetch_val('select min(id) from test') == 1

def test_fetch_col():
    assert fetch_col('select tag from test order by tag') == [10, 20]

def test_fetch_row():
    assert fetch_row('select * from test where id = 2') == (2, 20)

def test_fetch_all():
    assert fetch_all('select * from test order by id') == [(1, 10), (2, 20)]


def test_fetch_non_existent_row():
    assert fetch_row('select * from test where id < 0') is None

def test_fetch_non_existent_val():
    assert fetch_val('select tag from test where id < 0') is None


def test_fetch_dicts():
    rows = fetch_dicts('select * from test order by id')
    assert rows == [{'id': 1, 'tag': 10}, {'id': 2, 'tag': 20}]

def test_fetch_dict():
    row = fetch_dict('select * from test where id = 1')
    assert row == {'id': 1, 'tag': 10}


def test_fetch_named():
    rows = fetch_named('select * from test order by id')
    assert len(rows) == 2
    assert rows[0].id == 1 and rows[0].tag == 10
    assert rows[1].id == 2 and rows[1].tag == 20

def test_fetch_named_row():
    row = fetch_named_row('select * from test where id = 1')
    assert row == (1, 10)
    assert row.id == 1 and row.tag == 10

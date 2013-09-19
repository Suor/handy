import pytest

from handy.db import do_sql, fetch_all, fetch_row, fetch_col, fetch_val


def pytestmark(func):
    pytest.mark.django_db(func)
    pytest.mark.usefixtures('test_table')(func)


@pytest.fixture(scope='module')
def test_table():
    # NOTE: We wrap that into transaction because in other case django will gobble it up
    #       into single transaction with first test and then rollback everything happily on
    #       that tests end.
    do_sql('''
        begin;

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

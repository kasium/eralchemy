import pytest
from sqlalchemy import Column, ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, relationship

from eralchemy.models import Column as ERColumn
from eralchemy.models import Relation, Table

Base = declarative_base()


class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class Child(Base):
    __tablename__ = "child"
    id = Column(Integer, primary_key=True)
    parent_id = Column(ForeignKey("parent.id"))
    parent = relationship("Parent", backref="children")


class Exclude(Base):
    __tablename__ = "exclude"
    id = Column(Integer, primary_key=True)
    parent_id = Column(ForeignKey("parent.id"))
    parent = relationship("Parent", backref="excludes")


class ParentWithSchema(Base):
    __tablename__ = "parent"
    __table_args__ = {"schema": "eralchemy_test"}
    id = Column(Integer, primary_key=True)
    name = Column(String(255))


class ChildWithSchema(Base):
    __tablename__ = "child"
    __table_args__ = {"schema": "eralchemy_test"}
    id = Column(Integer, primary_key=True)
    parent_id = Column(ForeignKey("eralchemy_test.parent.id"))
    parent = relationship("ParentWithSchema", backref="eralchemy_test.children")


class ExcludeWithSchema(Base):
    __tablename__ = "exclude"
    __table_args__ = {"schema": "eralchemy_test"}
    id = Column(Integer, primary_key=True)
    parent_id = Column(ForeignKey("eralchemy_test.parent.id"))
    parent = relationship("ParentWithSchema", backref="eralchemy_test.excludes")


parent_id = ERColumn(name="id", type="INTEGER", is_key=True)

parent_name = ERColumn(
    name="name",
    type="VARCHAR(255)",
    is_null=True,
)

child_id = ERColumn(name="id", type="INTEGER", is_key=True)

child_parent_id = ERColumn(
    name="parent_id",
    type="INTEGER",
    is_null=True,
)

relation = Relation(
    right_col="parent",
    left_col="child",
    right_cardinality="?",
    left_cardinality="*",
)

exclude_id = ERColumn(name="id", type="INTEGER", is_key=True)

exclude_parent_id = ERColumn(
    name="parent_id",
    type="INTEGER",
)

exclude_relation = Relation(
    right_col="parent",
    left_col="exclude",
    right_cardinality="?",
    left_cardinality="*",
)

relationships = [relation, exclude_relation]

parent = Table(
    name="parent",
    columns=[parent_id, parent_name],
)

child = Table(
    name="child",
    columns=[child_id, child_parent_id],
)

exclude = Table(
    name="exclude",
    columns=[exclude_id, exclude_parent_id],
)

tables = [parent, child, exclude]

markdown = """
    [parent]
        *id {label:"INTEGER"}
        name {label:"VARCHAR(255)"}
    [child]
        *id {label:"INTEGER"}
        parent_id {label:"INTEGER"}
    [exclude]
        *id {label:"INTEGER"}
        parent_id {label:"INTEGER"}
    parent ?--* child
    parent ?--* exclude
    """


def assert_lst_equal(lst_actual, lst_expected):
    assert len(lst_actual) == len(lst_expected)
    for e in lst_actual:
        assert e in lst_expected


def check_intermediary_representation_simple_table(tables, relationships):
    """Check that that the tables and relationships represents the model above."""
    assert len(tables) == 3
    assert len(relationships) == 2
    assert all(isinstance(t, Table) for t in tables)
    assert all(isinstance(r, Relation) for r in relationships)
    assert relation in relationships
    assert exclude_relation in relationships


def check_intermediary_representation_simple_all_table(tables, relationships):
    # The Base know there are 6 tables because the tables are created with this Base.
    assert len(tables) == 6
    assert len(relationships) == 4
    assert all(isinstance(t, Table) for t in tables)
    assert all(isinstance(r, Relation) for r in relationships)
    assert relation in relationships
    assert exclude_relation in relationships


def check_tables_relationships(actual_tables, actual_relationships):
    assert len(actual_tables) == 2
    assert parent in actual_tables
    assert child in actual_tables
    assert len(actual_relationships) == 1
    assert relation in actual_relationships


def check_excluded_tables_relationships(actual_tables, actual_relationships):
    assert len(actual_tables) == 2
    assert parent in actual_tables
    assert child in actual_tables
    assert len(actual_relationships) == 1
    assert relation in actual_relationships


def check_tables_columns(actual_tables, id_is_included=True):
    assert len(actual_tables) == 3
    for t in actual_tables:
        columns_ = [c.name for c in t.columns]
        assert ("id" in columns_) == id_is_included
        assert len(t.columns) == 1


def check_filter(actual_tables, actual_relationships):
    assert actual_tables == tables
    assert actual_relationships == relationships
    assert [len(t.columns) for t in actual_tables] == [2, 2, 2]


@pytest.fixture
def sqlite_db_uri(db_uri="sqlite:///test.db"):
    engine = create_engine(db_uri)
    tables = [m.__table__ for m in (Parent, Child, Exclude)]
    Base.metadata.create_all(engine, tables=tables)
    return db_uri


@pytest.fixture
def pg_db_uri(
    db_uri="postgresql://eralchemy:eralchemy@localhost:5432/eralchemy",
):
    return db_uri

import re

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import MetaData
from sqlalchemy import String
from sqlalchemy import Table
from sqlalchemy.sql.sqltypes import DateTime

from alembic import autogenerate
from alembic.migration import MigrationContext
from alembic.testing import eq_
from alembic.testing import TestBase
from alembic.testing.suite._autogen_fixtures import _default_include_object
from alembic.testing.suite._autogen_fixtures import AutogenTest
from alembic.testing.suite._autogen_fixtures import ModelOne


class AutogenerateDiffTest(ModelOne, AutogenTest, TestBase):
    __only_on__ = "sqlite"

    def test_render_nothing(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                "compare_type": True,
                "compare_server_default": True,
                "target_metadata": self.m1,
                "upgrade_token": "upgrades",
                "downgrade_token": "downgrades",
            },
        )
        template_args = {}
        autogenerate._render_migration_diffs(context, template_args)

        eq_(
            re.sub(r"u'", "'", template_args["upgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###""",
        )
        eq_(
            re.sub(r"u'", "'", template_args["downgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###""",
        )

    def test_render_nothing_batch(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                "compare_type": True,
                "compare_server_default": True,
                "target_metadata": self.m1,
                "upgrade_token": "upgrades",
                "downgrade_token": "downgrades",
                "alembic_module_prefix": "op.",
                "sqlalchemy_module_prefix": "sa.",
                "render_as_batch": True,
                "include_symbol": lambda name, schema: False,
            },
        )
        template_args = {}
        autogenerate._render_migration_diffs(context, template_args)

        eq_(
            re.sub(r"u'", "'", template_args["upgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###""",
        )
        eq_(
            re.sub(r"u'", "'", template_args["downgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###""",
        )

    def test_render_diffs_standard(self):
        """test a full render including indentation"""

        template_args = {}
        autogenerate._render_migration_diffs(self.context, template_args)
        eq_(
            re.sub(r"u'", "'", template_args["upgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('len(description) > 5'),
    sa.ForeignKeyConstraint(['order_id'], ['order.order_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('extra')
    op.add_column('address', sa.Column('street', sa.String(length=50), \
nullable=True))
    op.create_unique_constraint('uq_email', 'address', ['email_address'])
    op.add_column('order', sa.Column('user_id', sa.Integer(), nullable=True))
    op.alter_column('order', 'amount',
               existing_type=sa.NUMERIC(precision=8, scale=2),
               type_=sa.Numeric(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text('0'))
    op.create_foreign_key(None, 'order', 'user', ['user_id'], ['id'])
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default='x',
               existing_nullable=True)
    op.drop_index('pw_idx', table_name='user')
    op.drop_column('user', 'pw')
    # ### end Alembic commands ###""",
        )

        eq_(
            re.sub(r"u'", "'", template_args["downgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('pw', sa.VARCHAR(length=50), \
nullable=True))
    op.create_index('pw_idx', 'user', ['pw'], unique=False)
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default=None,
               existing_nullable=True)
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.alter_column('order', 'amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.NUMERIC(precision=8, scale=2),
               nullable=False,
               existing_server_default=sa.text('0'))
    op.drop_column('order', 'user_id')
    op.drop_constraint('uq_email', 'address', type_='unique')
    op.drop_column('address', 'street')
    op.create_table('extra',
    sa.Column('x', sa.CHAR(), nullable=True),
    sa.Column('uid', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], )
    )
    op.drop_table('item')
    # ### end Alembic commands ###""",
        )

    def test_render_diffs_batch(self):
        """test a full render in batch mode including indentation"""

        template_args = {}
        self.context.opts["render_as_batch"] = True
        autogenerate._render_migration_diffs(self.context, template_args)

        eq_(
            re.sub(r"u'", "'", template_args["upgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('len(description) > 5'),
    sa.ForeignKeyConstraint(['order_id'], ['order.order_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('extra')
    with op.batch_alter_table('address', schema=None) as batch_op:
        batch_op.add_column(sa.Column('street', sa.String(length=50), nullable=True))
        batch_op.create_unique_constraint('uq_email', ['email_address'])

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.alter_column('amount',
               existing_type=sa.NUMERIC(precision=8, scale=2),
               type_=sa.Numeric(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text('0'))
        batch_op.create_foreign_key(None, 'user', ['user_id'], ['id'])

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)
        batch_op.alter_column('a1',
               existing_type=sa.TEXT(),
               server_default='x',
               existing_nullable=True)
        batch_op.drop_index('pw_idx')
        batch_op.drop_column('pw')

    # ### end Alembic commands ###""",  # noqa,
        )

        eq_(
            re.sub(r"u'", "'", template_args["downgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('pw', sa.VARCHAR(length=50), nullable=True))
        batch_op.create_index('pw_idx', ['pw'], unique=False)
        batch_op.alter_column('a1',
               existing_type=sa.TEXT(),
               server_default=None,
               existing_nullable=True)
        batch_op.alter_column('name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True)

    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.NUMERIC(precision=8, scale=2),
               nullable=False,
               existing_server_default=sa.text('0'))
        batch_op.drop_column('user_id')

    with op.batch_alter_table('address', schema=None) as batch_op:
        batch_op.drop_constraint('uq_email', type_='unique')
        batch_op.drop_column('street')

    op.create_table('extra',
    sa.Column('x', sa.CHAR(), nullable=True),
    sa.Column('uid', sa.INTEGER(), nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['user.id'], )
    )
    op.drop_table('item')
    # ### end Alembic commands ###""",  # noqa,
        )

    def test_imports_maintined(self):
        template_args = {}
        self.context.opts["render_as_batch"] = True

        def render_item(type_, col, autogen_context):
            autogen_context.imports.add(
                "from mypackage import my_special_import"
            )
            autogen_context.imports.add("from foobar import bat")

        self.context.opts["render_item"] = render_item
        autogenerate._render_migration_diffs(self.context, template_args)
        eq_(
            set(template_args["imports"].split("\n")),
            set(
                [
                    "from foobar import bat",
                    "from mypackage import my_special_import",
                ]
            ),
        )


class AddColumnOrderTest(AutogenTest, TestBase):
    @classmethod
    def _get_db_schema(cls):
        m = MetaData()

        Table(
            "user",
            m,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )

        return m

    @classmethod
    def _get_model_schema(cls):
        m = MetaData()

        Table(
            "user",
            m,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("username", String(50)),
            Column("password_hash", String(32)),
            Column("timestamp", DateTime),
        )

        return m

    def test_render_add_columns(self):
        """test #827"""

        template_args = {}
        autogenerate._render_migration_diffs(self.context, template_args)
        eq_(
            re.sub(r"u'", "'", template_args["upgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('username', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('password_hash', sa.String(length=32), nullable=True))
    op.add_column('user', sa.Column('timestamp', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###""",  # noqa E501
        )

        eq_(
            re.sub(r"u'", "'", template_args["downgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'timestamp')
    op.drop_column('user', 'password_hash')
    op.drop_column('user', 'username')
    # ### end Alembic commands ###""",
        )


class AutogenerateDiffTestWSchema(ModelOne, AutogenTest, TestBase):
    __only_on__ = "postgresql"
    schema = "test_schema"

    def test_render_nothing(self):
        context = MigrationContext.configure(
            connection=self.bind.connect(),
            opts={
                "compare_type": True,
                "compare_server_default": True,
                "target_metadata": self.m1,
                "upgrade_token": "upgrades",
                "downgrade_token": "downgrades",
                "alembic_module_prefix": "op.",
                "sqlalchemy_module_prefix": "sa.",
                "include_object": lambda name, *args: False,
            },
        )
        template_args = {}
        autogenerate._render_migration_diffs(context, template_args)

        eq_(
            re.sub(r"u'", "'", template_args["upgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###""",
        )
        eq_(
            re.sub(r"u'", "'", template_args["downgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###""",
        )

    def test_render_diffs_extras(self):
        """test a full render including indentation (include and schema)"""

        template_args = {}
        self.context.opts.update(
            {
                "include_object": _default_include_object,
                "include_schemas": True,
            }
        )
        autogenerate._render_migration_diffs(self.context, template_args)

        eq_(
            re.sub(r"u'", "'", template_args["upgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(length=100), nullable=True),
    sa.Column('order_id', sa.Integer(), nullable=True),
    sa.CheckConstraint('len(description) > 5'),
    sa.ForeignKeyConstraint(['order_id'], ['%(schema)s.order.order_id'], ),
    sa.PrimaryKeyConstraint('id'),
    schema='%(schema)s'
    )
    op.drop_table('extra', schema='%(schema)s')
    op.add_column('address', sa.Column('street', sa.String(length=50), \
nullable=True), schema='%(schema)s')
    op.create_unique_constraint('uq_email', 'address', ['email_address'], \
schema='test_schema')
    op.add_column('order', sa.Column('user_id', sa.Integer(), nullable=True), \
schema='%(schema)s')
    op.alter_column('order', 'amount',
               existing_type=sa.NUMERIC(precision=8, scale=2),
               type_=sa.Numeric(precision=10, scale=2),
               nullable=True,
               existing_server_default=sa.text('0'),
               schema='%(schema)s')
    op.create_foreign_key(None, 'order', 'user', ['user_id'], ['id'], \
source_schema='%(schema)s', referent_schema='%(schema)s')
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=False,
               schema='%(schema)s')
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default='x',
               existing_nullable=True,
               schema='%(schema)s')
    op.drop_index('pw_idx', table_name='user', schema='test_schema')
    op.drop_column('user', 'pw', schema='%(schema)s')
    # ### end Alembic commands ###"""
            % {"schema": self.schema},
        )

        eq_(
            re.sub(r"u'", "'", template_args["downgrades"]),
            """# ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('pw', sa.VARCHAR(length=50), \
autoincrement=False, nullable=True), schema='%(schema)s')
    op.create_index('pw_idx', 'user', ['pw'], unique=False, schema='%(schema)s')
    op.alter_column('user', 'a1',
               existing_type=sa.TEXT(),
               server_default=None,
               existing_nullable=True,
               schema='%(schema)s')
    op.alter_column('user', 'name',
               existing_type=sa.VARCHAR(length=50),
               nullable=True,
               schema='%(schema)s')
    op.drop_constraint(None, 'order', schema='%(schema)s', type_='foreignkey')
    op.alter_column('order', 'amount',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.NUMERIC(precision=8, scale=2),
               nullable=False,
               existing_server_default=sa.text('0'),
               schema='%(schema)s')
    op.drop_column('order', 'user_id', schema='%(schema)s')
    op.drop_constraint('uq_email', 'address', schema='test_schema', type_='unique')
    op.drop_column('address', 'street', schema='%(schema)s')
    op.create_table('extra',
    sa.Column('x', sa.CHAR(length=1), autoincrement=False, nullable=True),
    sa.Column('uid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['uid'], ['%(schema)s.user.id'], \
name='extra_uid_fkey'),
    schema='%(schema)s'
    )
    op.drop_table('item', schema='%(schema)s')
    # ### end Alembic commands ###"""  # noqa
            % {"schema": self.schema},
        )

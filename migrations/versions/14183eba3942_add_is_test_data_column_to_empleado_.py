"""Add is_test_data column to empleado table

Revision ID: 14183eba3942
Revises: 
Create Date: 2024-10-30 11:26:00.149257

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '14183eba3942'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    
    op.add_column('empleado', sa.Column('is_test_data', sa.Boolean(), nullable=True))
    op.alter_column('factura', 'subtotal',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, asdecimal=2),
               existing_nullable=False)
    op.alter_column('factura', 'total',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, asdecimal=2),
               existing_nullable=False)
    op.alter_column('factura', 'IVA',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, asdecimal=2),
               existing_nullable=False)
    op.alter_column('factura', 'descuento_aplicado',
               existing_type=sa.REAL(),
               type_=sa.Float(precision=10, asdecimal=2),
               existing_nullable=True)
    op.add_column('usuario', sa.Column('ultima_sesion', sa.DateTime(timezone=True), nullable=True))
    op.add_column('usuario', sa.Column('fecha_creacion', sa.DateTime(timezone=True), nullable=True))
    op.add_column('usuario', sa.Column('is_test_data', sa.Boolean(), nullable=True))
    op.alter_column('usuario', 'rol',
               existing_type=sa.VARCHAR(length=30),
               type_=sa.Enum('ADMIN', 'VENDEDOR', 'INVENTARIO', 'VISUALIZADOR', name='rolusuario'),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    
    op.alter_column('usuario', 'rol',
               existing_type=sa.Enum('ADMIN', 'VENDEDOR', 'INVENTARIO', 'VISUALIZADOR', name='rolusuario'),
               type_=sa.VARCHAR(length=30),
               existing_nullable=False)
    op.drop_column('usuario', 'is_test_data')
    op.drop_column('usuario', 'fecha_creacion')
    op.drop_column('usuario', 'ultima_sesion')
    op.alter_column('factura', 'descuento_aplicado',
               existing_type=sa.Float(precision=10, asdecimal=2),
               type_=sa.REAL(),
               existing_nullable=True)
    op.alter_column('factura', 'IVA',
               existing_type=sa.Float(precision=10, asdecimal=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('factura', 'total',
               existing_type=sa.Float(precision=10, asdecimal=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.alter_column('factura', 'subtotal',
               existing_type=sa.Float(precision=10, asdecimal=2),
               type_=sa.REAL(),
               existing_nullable=False)
    op.drop_column('empleado', 'is_test_data')
    op.create_table('categorias',
    sa.Column('id', sa.INTEGER(), server_default=sa.text("nextval('categorias_id_seq'::regclass)"), autoincrement=True, nullable=False),
    sa.Column('categoria', sa.VARCHAR(length=300), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='categorias_pkey'),
    sa.UniqueConstraint('categoria', name='categorias_categoria_key'),
    postgresql_ignore_search_path=False
    )
    op.create_table('detalle_factura',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('precio_unitario', sa.REAL(), autoincrement=False, nullable=False),
    sa.Column('cantidad', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('subtotal', sa.REAL(), autoincrement=False, nullable=False),
    sa.Column('id_factura', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_producto', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id_factura'], ['factura.id'], name='detalle_factura_id_factura_fkey'),
    sa.ForeignKeyConstraint(['id_producto'], ['productos.id'], name='detalle_factura_id_producto_fkey'),
    sa.PrimaryKeyConstraint('id', name='detalle_factura_pkey')
    )
    op.create_table('auditoria',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('tabla', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('accion', sa.VARCHAR(length=50), autoincrement=False, nullable=False),
    sa.Column('registro_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('usuario_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('detalles', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('fecha_hora', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='auditoria_pkey')
    )
    op.create_table('productos',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('nombre', sa.VARCHAR(length=55), autoincrement=False, nullable=True),
    sa.Column('genero', sa.VARCHAR(length=55), autoincrement=False, nullable=True),
    sa.Column('descripcion', sa.VARCHAR(length=300), autoincrement=False, nullable=False),
    sa.Column('stock', sa.REAL(), autoincrement=False, nullable=False),
    sa.Column('precio', sa.REAL(), autoincrement=False, nullable=False),
    sa.Column('categoria', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['categoria'], ['categorias.id'], name='productos_categoria_fkey'),
    sa.PrimaryKeyConstraint('id', name='productos_pkey'),
    sa.UniqueConstraint('descripcion', name='productos_descripcion_key')
    )
    # ### end Alembic commands ###

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import jsonify
from models import db, Warehouse, Item

warehouse_bp = Blueprint('warehouse', __name__)


@warehouse_bp.route('/')
def index():
    warehouses = Warehouse.query.all()
    return render_template('index.html', warehouses=warehouses)


@warehouse_bp.route('/warehouses', methods=['GET'])
def list_warehouses():
    warehouses = Warehouse.query.all()
    return jsonify([w.to_dict() for w in warehouses])


@warehouse_bp.route('/warehouses/<int:warehouse_id>', methods=['GET'])
def get_warehouse(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    return jsonify(warehouse.to_dict())


@warehouse_bp.route('/warehouses', methods=['POST'])
def create_warehouse():
    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        location = data.get('location', '')
        description = data.get('description', '')
    else:
        name = request.form.get('name')
        location = request.form.get('location', '')
        description = request.form.get('description', '')

    if not name or not name.strip():
        if request.is_json:
            return jsonify({'error': 'Name is required'}), 400
        flash('Name is required', 'error')
        return redirect(url_for('warehouse.index'))

    existing = Warehouse.query.filter_by(name=name.strip()).first()
    if existing:
        if request.is_json:
            return jsonify({'error': 'Warehouse name already exists'}), 400
        flash('Warehouse name already exists', 'error')
        return redirect(url_for('warehouse.index'))

    warehouse = Warehouse(
        name=name.strip(),
        location=location.strip() if location else '',
        description=description.strip() if description else ''
    )
    db.session.add(warehouse)
    db.session.commit()

    if request.is_json:
        return jsonify(warehouse.to_dict()), 201

    flash('Warehouse created successfully', 'success')
    return redirect(url_for('warehouse.index'))


@warehouse_bp.route('/warehouses/<int:warehouse_id>', methods=['PUT'])
def update_warehouse(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    data = request.get_json()

    if 'name' in data:
        new_name = data['name'].strip() if data['name'] else ''
        if not new_name:
            return jsonify({'error': 'Name cannot be empty'}), 400
        existing = Warehouse.query.filter_by(name=new_name).first()
        if existing and existing.id != warehouse_id:
            return jsonify({'error': 'Warehouse name already exists'}), 400
        warehouse.name = new_name

    if 'location' in data:
        warehouse.location = data['location'].strip() if data['location'] \
            else ''

    if 'description' in data:
        warehouse.description = data['description'].strip() \
            if data['description'] else ''

    db.session.commit()
    return jsonify(warehouse.to_dict())


@warehouse_bp.route(
    '/warehouses/<int:warehouse_id>/edit',
    methods=['GET', 'POST']
)
def edit_warehouse(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)

    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location', '')
        description = request.form.get('description', '')

        if not name or not name.strip():
            flash('Name is required', 'error')
            return render_template(
                'edit_warehouse.html', warehouse=warehouse
            )

        existing = Warehouse.query.filter_by(name=name.strip()).first()
        if existing and existing.id != warehouse_id:
            flash('Warehouse name already exists', 'error')
            return render_template(
                'edit_warehouse.html', warehouse=warehouse
            )

        warehouse.name = name.strip()
        warehouse.location = location.strip() if location else ''
        warehouse.description = description.strip() if description else ''
        db.session.commit()

        flash('Warehouse updated successfully', 'success')
        return redirect(url_for('warehouse.index'))

    return render_template('edit_warehouse.html', warehouse=warehouse)


@warehouse_bp.route('/warehouses/<int:warehouse_id>', methods=['DELETE'])
def delete_warehouse(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    db.session.delete(warehouse)
    db.session.commit()
    return jsonify({'message': 'Warehouse deleted successfully'}), 200


@warehouse_bp.route(
    '/warehouses/<int:warehouse_id>/delete',
    methods=['POST']
)
def delete_warehouse_form(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)
    db.session.delete(warehouse)
    db.session.commit()
    flash('Warehouse deleted successfully', 'success')
    return redirect(url_for('warehouse.index'))


@warehouse_bp.route(
    '/warehouses/<int:warehouse_id>/items',
    methods=['POST']
)
def add_item(warehouse_id):
    warehouse = Warehouse.query.get_or_404(warehouse_id)

    if request.is_json:
        data = request.get_json()
        name = data.get('name')
        quantity = data.get('quantity', 0.0)
    else:
        name = request.form.get('name')
        quantity = request.form.get('quantity', 0.0)

    if not name or not str(name).strip():
        if request.is_json:
            return jsonify({'error': 'Item name is required'}), 400
        flash('Item name is required', 'error')
        return redirect(url_for('warehouse.view_warehouse', w_id=warehouse_id))

    try:
        quantity = float(quantity)
    except (ValueError, TypeError):
        quantity = 0.0

    if quantity < 0:
        if request.is_json:
            return jsonify({'error': 'Quantity cannot be negative'}), 400
        flash('Quantity cannot be negative', 'error')
        return redirect(url_for('warehouse.view_warehouse', w_id=warehouse_id))

    item = Item(
        name=str(name).strip(),
        quantity=quantity,
        warehouse_id=warehouse.id
    )
    db.session.add(item)
    db.session.commit()

    if request.is_json:
        return jsonify(item.to_dict()), 201

    flash('Item added successfully', 'success')
    return redirect(url_for('warehouse.view_warehouse', w_id=warehouse_id))


@warehouse_bp.route(
    '/warehouses/<int:warehouse_id>/items/<int:item_id>',
    methods=['DELETE']
)
def remove_item(warehouse_id, item_id):
    item = Item.query.filter_by(
        id=item_id, warehouse_id=warehouse_id
    ).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item removed successfully'}), 200


@warehouse_bp.route(
    '/warehouses/<int:warehouse_id>/items/<int:item_id>/delete',
    methods=['POST']
)
def remove_item_form(warehouse_id, item_id):
    item = Item.query.filter_by(
        id=item_id, warehouse_id=warehouse_id
    ).first()
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('warehouse.view_warehouse', w_id=warehouse_id))

    db.session.delete(item)
    db.session.commit()
    flash('Item removed successfully', 'success')
    return redirect(url_for('warehouse.view_warehouse', w_id=warehouse_id))


@warehouse_bp.route('/warehouses/<int:w_id>/view')
def view_warehouse(w_id):
    warehouse = Warehouse.query.get_or_404(w_id)
    return render_template('view_warehouse.html', warehouse=warehouse)

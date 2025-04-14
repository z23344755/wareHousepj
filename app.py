
# 货架
#A 排第一个货架 A层
#A1A

# 地堆
# A1 : A3

#  http://192.168.56.1:8848/IT-Project/index2.html
# #  http://192.168.1.18:8848/IT-Project/index2.html
from flask import Flask , render_template ,jsonify ,request
import psycopg2
from psycopg2 import extras  # 导入 extras 模块
from flask_cors import CORS  # 导入 CORS

import pandas as pd
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2 import extras

import db_util

app = Flask(__name__)
CORS(app)


@app.route('/')
def home_page():
    return render_template('index.html')


@app.route('/sku.html')
def sku_page():
    return render_template('sku.html')


@app.route('/map.html')
def map_page():
    return render_template('map.html')


@app.route('/in_out_history.html')
def in_out_history_page():
    return render_template('in_out_history.html')


@app.route('/inventory.html')
def inventory_page():
    return render_template('inventory.html')

# 获取库存
@app.route('/hello')
def test_hello():
    return render_template('hello123.html')


@app.route('/api/sku')
def get_sku():
    con = db_util.get_db_connecttion()

    #cursor = con.cursor()
    #TODO
    cursor = con.cursor(cursor_factory=extras.DictCursor)

    #cursor.execute("SELECT sku.* , sum(inventory.quantity) as quantity from sku left join inventory on sku.sku_code = inventory.sku_code group by sku.id, sku.sku_code, name, description, company,created_at ")

    cursor.execute("SELECT sku.* from sku  order by sku_code   ")

    rows = cursor.fetchall()
    print(rows)
    # TODO
    #result = [dict(row) for row in rows]
    result = []
    for row in rows:
        result.append(dict(row))

    con.close()

    return jsonify(result)


@app.route('/api/sku/update', methods=['POST'])
def update_sku():
    # Get the request data
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    sku_code = data.get('sku_code')
    if not sku_code:
        return jsonify({"error": "sku_code is required"}), 400

    # Extract fields to update
    name = data.get('name')
    description = data.get('description')
    company = data.get('company')
    quantity = data.get('quantity')

    # Validate at least one field is provided
    if not any([name, description, company, quantity is not None]):
        return jsonify({"error": "No fields to update provided"}), 400

    # Validate quantity is non-negative if provided
    if quantity is not None and quantity < 0:
        return jsonify({"error": "Quantity must be non-negative"}), 400

    con = db_util.get_db_connecttion()
    try:
        cursor = con.cursor()
        # Build the dynamic update query
        update_fields = []
        params = []

        if name is not None:
            update_fields.append("name = %s")
            params.append(name)
        if description is not None:
            update_fields.append("description = %s")
            params.append(description)
        if company is not None:
            update_fields.append("company = %s")
            params.append(company)
        if quantity is not None:
            update_fields.append("quantity = %s")
            params.append(quantity)

        # Add sku_code to params for WHERE clause
        params.append(sku_code)

        update_query = f"""
            UPDATE sku 
            SET {', '.join(update_fields)}
            WHERE sku_code = %s
        """

        cursor.execute(update_query, params)

        con.commit()


        return jsonify({
            "message": "SKU updated successfully",
        }), 200

    except Exception as e:
        con.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        con.close()


@app.route('/api/sku/delete', methods=['POST'])
def delete_sku():
    # Get the request data
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    sku_code = data.get('sku_code')
    if not sku_code:
        return jsonify({"error": "sku_code is required"}), 400

    con = db_util.get_db_connecttion()
    try:
        cursor = con.cursor()

        # First check if the SKU exists
        cursor.execute("SELECT 1 FROM sku WHERE sku_code = %s", (sku_code,))
        if not cursor.fetchone():
            return jsonify({"error": "SKU not found"}), 404

        # Delete the SKU
        delete_query = "DELETE FROM sku WHERE sku_code = %s"
        cursor.execute(delete_query, (sku_code,))

        con.commit()

        return jsonify({
            "message": "SKU deleted successfully",
            "sku_code": sku_code
        }), 200

    except Exception as e:
        con.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        con.close()



# {  'id': 5,
#    'sku:' "SKU005",
#    "product" :"Product E",
# "product": "Innovative product E designed for tech enthusiasts",
#     "Company Y",
#     "Thu, 05 Oct 2023 16:20:00 GMT"
# }



@app.route('/api/in_out_history')
def get_in_out_history():
    # 获取请求参数中的 sku_code
    sku_code = request.args.get('sku_code')
    if not sku_code:
        return jsonify({"error": "sku_code is required"}), 400

    # 连接数据库
    con = db_util.get_db_connecttion()


    # 使用 DictCursor 游标
    cursor = con.cursor(cursor_factory=extras.DictCursor)

    try:
        # 查询指定 sku_code 的出入库记录
        cursor.execute("""
            SELECT * FROM in_out_his
            WHERE sku_code = %s
            ORDER BY operate_time DESC
        """, (sku_code,))

        rows = cursor.fetchall()

        # 将查询结果转换为字典列表
        result = [dict(row) for row in rows]

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # 关闭数据库连接
        cursor.close()
        con.close()


@app.route('/api/inventory')
def get_inventory():
    # 连接数据库
    con = db_util.get_db_connecttion()


    # 使用 DictCursor 游标
    cursor = con.cursor(cursor_factory=extras.DictCursor)

    # 查询仓库位置和库存信息
    cursor.execute("""
        SELECT 
            wl.id, 
            wl.type, 
            wl.location, 
            wl.bounds,
            inv.id AS inventory_id,
            inv.sku_code,
            inv.quantity,
            inv.update_time,
            inv.level
        FROM warehouse_locations wl
        LEFT JOIN inventory inv ON wl.location = inv.warehouse_location
        ORDER BY wl.location, inv.sku_code
    """)

    rows = cursor.fetchall()

    # 处理查询结果，按位置分组
    inventory_map = {}
    for row in rows:
        location_id = row['id']
        if location_id not in inventory_map:
            # 解析bounds为坐标数组
            bounds_coords = row['bounds'].split(',')
            bounds_formatted = [
                [int(bounds_coords[0].strip()), int(bounds_coords[1].strip())],  # 左下角
                [int(bounds_coords[2].strip()), int(bounds_coords[3].strip())]  # 右上角
            ]

            inventory_map[location_id] = {
                'id': location_id,
                'type': row['type'],
                'bounds': bounds_formatted,
                'location': row['location'],
                'skus': []
            }

        # 添加SKU信息（如果有库存记录）
        if row['sku_code']:
            inventory_map[location_id]['skus'].append({
                'sku': row['sku_code'],
                'count': row['quantity'],
                'level': row['level'],
                'inventory_id': row['inventory_id']
            })
    # 转换为列表格式
    result = list(inventory_map.values())

    cursor.close()
    con.close()

    return jsonify(result)





@app.route('/api/upload_inventory', methods=['POST'])
def upload_inventory():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Check if file has a valid name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Secure the filename and check if it's an Excel file
    filename = secure_filename(file.filename)
    if not (filename.endswith('xlsx') or filename.endswith('xls')):
        return jsonify({"error": "Only Excel files are allowed"}), 400

    try:
        # Read the Excel file
        df = pd.read_excel(file)

        # Validate required columns
        required_columns = ['sku_code', 'quantity', 'warehouse_location', 'level']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"Excel file must contain columns: {', '.join(required_columns)}"}), 400

        # Connect to database
        con = db_util.get_db_connecttion()

        cursor = con.cursor(cursor_factory=extras.DictCursor)

        # Process each row in the Excel file
        for _, row in df.iterrows():
            sku_code = row['sku_code']
            quantity = row['quantity']
            warehouse_location = row['warehouse_location']
            level = row['level']

            # Validate quantity
            if quantity <= 0:
                continue  # Skip invalid quantities or you could return an error

            try:
                # 1. 处理SKU表 - 先查询是否存在
                cursor.execute("SELECT id, quantity FROM sku WHERE sku_code = %s", (sku_code,))
                sku_record = cursor.fetchone()

                if sku_record:
                    # 更新现有SKU
                    new_quantity = sku_record['quantity'] + quantity
                    cursor.execute("""
                        UPDATE sku SET quantity = %s WHERE id = %s
                    """, (new_quantity, sku_record['id']))
                else:
                    # 插入新SKU
                    cursor.execute("""
                        INSERT INTO sku (sku_code, quantity)
                        VALUES (%s, %s)
                    """, (sku_code, quantity))

                # 2. 处理Inventory表 - 先查询是否存在
                cursor.execute("""
                    SELECT id, quantity FROM inventory 
                    WHERE sku_code = %s AND warehouse_location = %s AND level = %s
                """, (sku_code, warehouse_location, level))
                inv_record = cursor.fetchone()

                if inv_record:
                    # 更新现有库存记录
                    new_quantity = inv_record['quantity'] + quantity
                    cursor.execute("""
                        UPDATE inventory 
                        SET quantity = %s, update_time = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (new_quantity, inv_record['id']))
                else:
                    # 插入新库存记录
                    cursor.execute("""
                        INSERT INTO inventory (sku_code, quantity, warehouse_location, level)
                        VALUES (%s, %s, %s, %s)
                    """, (sku_code, quantity, warehouse_location, level))

                # 3. 插入历史记录 (始终新增)
                cursor.execute("""
                    INSERT INTO in_out_his (sku_code, operate_type, quantity, warehouse_location, level)
                    VALUES (%s, 'in', %s, %s, %s)
                """, (sku_code, quantity, warehouse_location, level))

                con.commit()

            except Exception as e:
                con.rollback()
                return jsonify({
                    "error": f"Failed to process SKU {sku_code}",
                    "details": str(e)
                }), 500

        return jsonify({"message": "Inventory updated successfully"}), 200

    except pd.errors.EmptyDataError:
        return jsonify({"error": "Excel file is empty"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()


@app.route('/api/upload_outbound', methods=['POST'])
def upload_outbound():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Check if file has a valid name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Secure the filename and check if it's an Excel file
    filename = secure_filename(file.filename)
    if not (filename.endswith('xlsx') or filename.endswith('xls')):
        return jsonify({"error": "Only Excel files are allowed"}), 400

    try:
        # Read the Excel file
        df = pd.read_excel(file)

        # Validate required columns
        required_columns = ['sku_code', 'quantity']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"Excel file must contain columns: {', '.join(required_columns)}"}), 400

        # Connect to database
        con = db_util.get_db_connecttion()

        cursor = con.cursor(cursor_factory=extras.DictCursor)

        # Process each row in the Excel file
        for _, row in df.iterrows():
            sku_code = row['sku_code']
            quantity = row['quantity']

            # Validate quantity
            if quantity <= 0:
                continue  # Skip invalid quantities

            try:
                # 1. Check current stock quantity
                cursor.execute("SELECT id, quantity FROM sku WHERE sku_code = %s FOR UPDATE", (sku_code,))
                sku_record = cursor.fetchone()

                if not sku_record:
                    raise Exception(f"SKU {sku_code} not found")

                current_quantity = sku_record['quantity']
                if current_quantity < quantity:
                    raise Exception(
                        f"Insufficient stock for SKU {sku_code}. Available: {current_quantity}, Requested: {quantity}")

                # 2. Update SKU table (reduce quantity)
                new_quantity = current_quantity - quantity
                cursor.execute("""
                    UPDATE sku SET quantity = %s WHERE id = %s
                """, (new_quantity, sku_record['id']))

                # 3. Insert outbound record
                cursor.execute("""
                    INSERT INTO in_out_his 
                    (sku_code, operate_type, quantity)
                    VALUES (%s, 'out', %s)
                """, (sku_code, quantity))

                con.commit()

            except Exception as e:
                con.rollback()
                return jsonify({
                    "error": f"Failed to process outbound for SKU {sku_code}",
                    "details": str(e)
                }), 500

        return jsonify({"message": "Outbound processed successfully"}), 200

    except pd.errors.EmptyDataError:
        return jsonify({"error": "Excel file is empty"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()





@app.route('/api/upload_skus', methods=['POST'])
def upload_skus():
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']

    # Check if file has a valid name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Secure the filename and check if it's an Excel file
    filename = secure_filename(file.filename)
    if not (filename.endswith('xlsx') or filename.endswith('xls')):
        return jsonify({"error": "Only Excel files are allowed"}), 400

    try:
        # Read the Excel file
        df = pd.read_excel(file)

        # Validate required columns (根据sku表的字段)
        required_columns = ['sku_code', 'name', 'description', 'company']
        if not all(col in df.columns for col in required_columns):
            return jsonify({"error": f"Excel file must contain columns: {', '.join(required_columns)}"}), 400

        # Connect to database
        con = db_util.get_db_connecttion()
        cursor = con.cursor(cursor_factory=extras.DictCursor)

        # 统计变量
        inserted_count = 0
        updated_count = 0
        skipped_count = 0

        # Process each row in the Excel file
        for _, row in df.iterrows():
            sku_code = row['sku_code']
            name = row.get('name', '')
            description = row.get('description', '')
            company = row.get('company', '')

            try:
                # 检查SKU是否已存在
                cursor.execute("SELECT id FROM sku WHERE sku_code = %s", (sku_code,))
                sku_record = cursor.fetchone()

                if sku_record:
                    # 更新现有SKU（不更新quantity字段）
                    cursor.execute("""
                        UPDATE sku 
                        SET name = %s, 
                            description = %s, 
                            company = %s
                        WHERE id = %s
                    """, (name, description, company, sku_record['id']))
                    updated_count += 1
                else:
                    # 插入新SKU（quantity使用默认值0）
                    cursor.execute("""
                        INSERT INTO sku (sku_code, name, description, company, quantity)
                        VALUES (%s, %s, %s, %s, 0)
                    """, (sku_code, name, description, company))
                    inserted_count += 1

                con.commit()

            except Exception as e:
                con.rollback()
                skipped_count += 1
                # 可以选择记录错误日志
                print(f"Error processing SKU {sku_code}: {str(e)}")

        return jsonify({
            "message": "SKU import completed",
            "stats": {
                "inserted": inserted_count,
                "updated": updated_count,
                "skipped": skipped_count
            }
        }), 200

    except pd.errors.EmptyDataError:
        return jsonify({"error": "Excel file is empty"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'con' in locals():
            con.close()




@app.route('/api/inventory/update', methods=['POST'])
def update_inventory():
    # Get the request data
    data = request.get_json()

    # Validate required fields
    if not data:
        return jsonify({"error": "No data provided"}), 400

    inventory_id = data.get('id')
    if not inventory_id:
        return jsonify({"error": "id is required"}), 400

    # Extract fields to update
    sku_code = data.get('sku_code')
    quantity = data.get('quantity')
    if quantity is not  None:
        quantity = int(quantity)
    level = data.get('level')

    # Validate at least one field is provided
    if not any([sku_code, quantity is not None, level]):
        return jsonify({"error": "No fields to update provided"}), 400

    # Validate quantity is non-negative if provided
    if quantity is not None and quantity < 0:
        return jsonify({"error": "Quantity must be non-negative"}), 400

    con = db_util.get_db_connecttion()
    cursor = con.cursor()
    # Build the dynamic update query
    update_fields = []
    params = []

    if sku_code is not None:
        update_fields.append("sku_code = %s")
        params.append(sku_code)
    if quantity is not None:
        update_fields.append("quantity = %s")
        params.append(quantity)
    if level is not None:
        update_fields.append("level = %s")
        params.append(level)

    # Always update the update_time
    update_fields.append("update_time = CURRENT_TIMESTAMP")

    # Add inventory_id to params for WHERE clause
    params.append(inventory_id)

    update_query = f"""
        UPDATE inventory 
        SET {', '.join(update_fields)}
        WHERE id = %s
    """

    cursor.execute(update_query, params)

    con.commit()

    con.close()

    return jsonify({
        "message": "Inventory updated successfully",
    }), 200









if __name__ == '__main__':
    app.run(debug=False)
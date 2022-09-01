# Determines how many and which users will be stored in orders_fix.csv based on different product purchases
user_count = 2000
product_count = 10000
product_prior_count = 20

# Initialize and declare paths of data files
path_orders = "orders.csv"
path_order_products = "order_products__prior.csv"
path_products = "products.csv"
path_aisles = "aisles.csv"
path_departments = "departments.csv"


# Initialize and declare dictionaries to store data lines
user_orders = {}
order_products_prior = {}
order_products_last = {}
products = []
aisles = []
departments = []

# Initialize and declare helper set and dictionaries for storing user ids and data connections
id_users = set()
id_aisles = set()
id_departments = set()
id_products = set()
order_to_user_prior = {}
order_to_user_last = {}
user_products = {}
product_users_count = {}

# Orders read
print("Reading data:")
print("Reading order.csv file...")

# Open file to read
with open(path_orders, mode="r", encoding="utf-8") as f:
    saved_order_id = ""
    # Read lines in file (ignore heading)
    for line in f.readlines()[1:]:
        line_split = line.split(",")
        order_id = line_split[0]
        user_id = line_split[1]
        # Adds an user id, order id and order line to the dictionaries if eval_set attribute has a prior value
        if line_split[2] == 'prior':
            order_to_user_prior[order_id] = user_id
            if user_id not in user_orders:
                user_orders[user_id] = []
            user_orders[user_id].append(line)
            saved_order_id = order_id
        # INFO: The last order with the value "prior" in the eval_set attribute is used as the user's last order,
        #       because the "train" and "test" orders (actually the users' last orders) are missing products
        #       (the "test" orders are only found if the program is running on Kaggle)
        else:
            user_id = order_to_user_prior.pop(saved_order_id)
            order_to_user_last[saved_order_id] = user_id
            user_orders[user_id][-1] = user_orders[user_id][-1].replace(",prior,", ",last,")

# Order products read
print("Finished reading order.csv file.")
print("Reading order_products__prior.csv file...")

# Open file to read
with open(path_order_products, mode="r", encoding="utf-8") as f:
    # Read lines in file (ignore heading)
    for line in f.readlines()[1:]:
        line_split = line.split(",")
        order_id = line_split[0]
        product_id = line_split[1]
        user_id = None
        if order_id in order_to_user_prior:
            # Adds a product order line to the dictionary of prior orders
            user_id = order_to_user_prior[order_id]
            if order_id not in order_products_prior:
                order_products_prior[order_id] = []
            order_products_prior[order_id].append(line)
            # Adds a product to the dictionary of prior purchases
            if user_id not in user_products:
                user_products[user_id] = {"prior": set(), "last": set()}
            user_products[user_id]["prior"].add(product_id)
        else:
            # Adds a product order line to the dictionary of last orders
            user_id = order_to_user_last[order_id]
            if order_id not in order_products_last:
                order_products_last[order_id] = []
            order_products_last[order_id].append(line)
            # Adds a product to the dictionary of prior purchases
            if user_id not in user_products:
                user_products[user_id] = {"prior": set(), "last": set()}
            user_products[user_id]["last"].add(product_id)
        # Adds the user to the dictionary of products
        if product_id not in product_users_count:
            product_users_count[product_id] = set()
        product_users_count[product_id].add(user_id)

# Products read
print("Finished reading order_products__prior.csv file.")
print("Reading products.csv file...")

# Get the products with most distinct purchases (determined by product_count)
product_users_count = {k: v for k, v in sorted(product_users_count.items(), key=lambda item: len(item[1]))}
for count in range(product_count):
    temp_item = product_users_count.popitem()
    id_products.add(temp_item[0])

# Open file to read.
with open(path_products, mode="r", encoding="utf-8") as f:
    # Read lines in file (ignore heading).
    for line in f.readlines()[1:]:
        # Check if the product is valid
        if line.split(",")[0] in id_products:
            # Delete quotes from a line
            # Delete comma from a line if its between two quotes
            line_list = list(line)
            delete_commas = False
            for i in range(0, len(line_list)):
                if line_list[i] == "\"":
                    line_list[i] = ""
                    delete_commas = not delete_commas
                if delete_commas and line_list[i] == ",":
                    line_list[i] = ";"
            # Add modified line to the list
            line_split = "".join(line_list).split(",")
            products.append(f"{line_split[0]},{line_split[1]},{line_split[2]},{line_split[3]}")
            id_aisles.add(line_split[2])
            id_departments.add(line_split[3].replace("\n", ""))

# Aisle read
print("Finished reading products.csv file.")
print("Reading aisle.csv file...")

# Open file to read.
with open(path_aisles, mode="r", encoding="utf-8") as f:
    # Read lines in file (ignore heading).
    for line in f.readlines()[1:]:
        if line.split(",")[0] in id_aisles:
            aisles.append(line)

# Department read
print("Finished reading aisle.csv file.")
print("Reading department.csv file...")

# Open file to read.
with open(path_departments, mode="r", encoding="utf-8") as f:
    # Read lines in file (ignore heading).
    for line in f.readlines()[1:]:
        if line.split(",")[0] in id_departments:
            departments.append(line)

# Orders construct
print("Finished reading department.csv file.\n")
print("Creating modified data:")
print("Creating modified orders.csv file...")

# Open file to write
with open("modified/orders.csv", mode="w", encoding="utf-8") as f:
    f.write("order_id,user_id,eval_set,order_number,order_dow,order_hour_of_day,days_since_prior_order\n")
    # Read lines in 'user_orders' variable
    for user_id, lines in user_orders.items():
        # Check user count
        if len(id_users) >= user_count:
            break
        # Check product count
        if len(user_products[user_id]["prior"]) >= product_prior_count and not user_products[user_id]["prior"].union(user_products[user_id]["last"]).difference(id_products):
            id_users.add(user_id)
            # Write line in file
            for line in lines:
                f.write(f"{line}")

# Order products 'prior' construct
print("Modified file orders.csv created.")
print("Creating modified order_products_prior.csv file...")

# Open file to write
with open("modified/order_products_prior.csv", mode="w", encoding="utf-8") as f:
    f.write("order_id,product_id,add_to_cart_order,reordered\n")
    # Read lines in 'order_products_prior' variable
    for order_id, lines in order_products_prior.items():
        user_id = order_to_user_prior[order_id]
        # Check if it is the right user
        if user_id in id_users:
            # Write line in file
            for line in lines:
                # Write line in file
                f.write(f"{line}")

# Order products 'last' construct
print("Modified file order_products_prior.csv created.")
print("Creating modified order_products_last.csv file...")

# Open file to write
with open("modified/order_products_last.csv", mode="w", encoding="utf-8") as f:
    f.write("order_id,product_id,add_to_cart_order,reordered\n")
    # Read lines in 'order_products_last' variable
    for order_id, lines in order_products_last.items():
        user_id = order_to_user_last[order_id]
        # Check if it is the right user
        if user_id in id_users:
            # Write line in file
            for line in lines:
                # Write line in file
                f.write(f"{line}")

# Products construct
print("Modified file order_products_last.csv created.")
print("Creating modified products.csv file...")

# Open file to write.
with open("modified/products.csv", mode="w", encoding="utf-8") as f:
    f.write("product_id,product_name,aisle_id,department_id\n")
    # Read lines in 'products' variable
    for line in products:
        # Write line in file.
        f.write(f"{line}")

# Products construct
print("Modified file products.csv created.")
print("Creating modified aisles.csv file...")

# Open file to write.
with open("modified/aisles.csv", mode="w", encoding="utf-8") as f:
    f.write("aisle_id,aisle\n")
    # Read lines in 'aisles' variable
    for line in aisles:
        # Write line in file.
        f.write(f"{line}")

# Products construct
print("Modified file aisles.csv created.")
print("Creating modified departments.csv file...")

# Open file to write.
with open("modified/departments.csv", mode="w", encoding="utf-8") as f:
    f.write("department_id,department\n")
    # Read lines in 'departments' variable
    for line in departments:
        # Write line in file.
        f.write(f"{line}")

# End of program
print("Modified file departments.csv created.\n")

# Test
print("Testing modified data:")
print(f"Users counted: {len(id_users)}")
print(f"Products counted: {len(id_products)}")
print(f"Aisles counted: {len(id_aisles)}")
print(f"Departments counted: {len(id_departments)}")
test_order_count = {}
test_product_count = {}
sum_distinct_purchase = 0
for user_id, lines in user_orders.items():
    if user_id in id_users:
        temp_order_count = len(lines)
        if temp_order_count not in test_order_count:
            test_order_count[temp_order_count] = set()
        test_order_count[temp_order_count].add(user_id)
        temp_product_count = len(user_products[user_id]["prior"])
        sum_distinct_purchase += temp_product_count
        if temp_product_count not in test_product_count:
            test_product_count[temp_product_count] = set()
        test_product_count[temp_product_count].add(user_id)
print(f"Min orders: {min(test_order_count)} | Users: {test_order_count[min(test_order_count)]}")
print(f"Max orders: {max(test_order_count)} | Users: {test_order_count[max(test_order_count)]}")
print(f"Distinct purchases of min prior products: {min(test_product_count)} | Users: {test_product_count[min(test_product_count)]}")
print(f"Distinct purchases of max prior products: {max(test_product_count)} | Users: {test_product_count[max(test_product_count)]}")
print(f"The avg number of distinct purchases of a product: {sum_distinct_purchase / len(id_products)}")

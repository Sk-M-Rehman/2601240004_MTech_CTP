# ==========================================
#       SHOPPING CART MANAGEMENT SYSTEM
# ==========================================

cart = []

GST_RATE = 18
DISCOUNT_RATE = 10

while True:

    print("\n================================")
    print("       SHOPPING CART SYSTEM")
    print("================================")
    print("1. Add Product")
    print("2. Remove Product")
    print("3. Change Quantity")
    print("4. Display Cart")
    print("5. Apply Discount")
    print("6. Calculate Final Bill")
    print("7. Exit")
    print("================================")

    choice = input("Enter your choice: ")

    # --------------------------------------
    # 1. Add Product
    # --------------------------------------
    if choice == "1":

        product_name = input("Enter product name: ")
        price = float(input("Enter product price: "))
        quantity = int(input("Enter quantity: "))

        # Check if product already exists
        product_found = False

        for product in cart:

            if product["name"].lower() == product_name.lower():

                product["quantity"] += quantity
                product_found = True

                print("Product quantity updated.")

                break

        # Add new product
        if product_found == False:

            product = {
                "name": product_name,
                "price": price,
                "quantity": quantity
            }

            cart.append(product)

            print("Product added to cart.")


    # --------------------------------------
    # 2. Remove Product
    # --------------------------------------
    elif choice == "2":

        product_name = input("Enter product name to remove: ")

        product_found = False

        for product in cart:

            if product["name"].lower() == product_name.lower():

                cart.remove(product)

                product_found = True

                print("Product removed from cart.")

                break

        if product_found == False:
            print("Product not found in cart.")


    # --------------------------------------
    # 3. Change Quantity
    # --------------------------------------
    elif choice == "3":

        product_name = input("Enter product name: ")
        new_quantity = int(input("Enter new quantity: "))

        product_found = False

        for product in cart:

            if product["name"].lower() == product_name.lower():

                if new_quantity > 0:

                    product["quantity"] = new_quantity
                    print("Quantity updated.")

                else:

                    cart.remove(product)
                    print("Product removed from cart.")

                product_found = True

                break

        if product_found == False:
            print("Product not found in cart.")


    # --------------------------------------
    # 4. Display Cart
    # --------------------------------------
    elif choice == "4":

        if len(cart) == 0:

            print("\nYour cart is empty.")

        else:

            print("\n==============================================")
            print("                 SHOPPING CART")
            print("==============================================")

            print(
                "Product\t\tPrice\tQuantity\tTotal"
            )

            print("----------------------------------------------")

            for product in cart:

                total = product["price"] * product["quantity"]

                print(
                    product["name"],
                    "\t\t₹", product["price"],
                    "\t", product["quantity"],
                    "\t\t₹", total
                )


    # --------------------------------------
    # 5. Apply Discount
    # --------------------------------------
    elif choice == "5":

        if len(cart) == 0:

            print("Cart is empty.")

        else:

            subtotal = 0

            for product in cart:

                subtotal += (
                    product["price"] *
                    product["quantity"]
                )

            discount = subtotal * DISCOUNT_RATE / 100

            amount_after_discount = subtotal - discount

            print("\nSubtotal: ₹", round(subtotal, 2))
            print(
                "Discount (",
                DISCOUNT_RATE,
                "%): ₹",
                round(discount, 2)
            )
            print(
                "Amount after discount: ₹",
                round(amount_after_discount, 2)
            )


    # --------------------------------------
    # 6. Calculate Final Bill
    # --------------------------------------
    elif choice == "6":

        if len(cart) == 0:

            print("Cart is empty.")

        else:

            # Calculate subtotal
            subtotal = 0

            for product in cart:

                total = (
                    product["price"] *
                    product["quantity"]
                )

                subtotal += total


            # Calculate discount
            discount = (
                subtotal *
                DISCOUNT_RATE /
                100
            )


            # Amount after discount
            amount_after_discount = (
                subtotal - discount
            )


            # Calculate GST
            gst = (
                amount_after_discount *
                GST_RATE /
                100
            )


            # Final bill
            final_bill = (
                amount_after_discount +
                gst
            )


            print("\n")
            print("==============================================")
            print("                 FINAL BILL")
            print("==============================================")

            print(
                "Product\t\tPrice\tQty\tTotal"
            )

            print("----------------------------------------------")

            for product in cart:

                total = (
                    product["price"] *
                    product["quantity"]
                )

                print(
                    product["name"],
                    "\t\t₹", product["price"],
                    "\t", product["quantity"],
                    "\t₹", round(total, 2)
                )

            print("----------------------------------------------")

            print("Subtotal              : ₹", round(subtotal, 2))
            print(
                "Discount (10%)        : ₹",
                round(discount, 2)
            )
            print(
                "Amount after Discount : ₹",
                round(amount_after_discount, 2)
            )
            print(
                "GST (18%)             : ₹",
                round(gst, 2)
            )
            print("----------------------------------------------")
            print(
                "FINAL BILL            : ₹",
                round(final_bill, 2)
            )
            print("==============================================")


    # --------------------------------------
    # 7. Exit
    # --------------------------------------
    elif choice == "7":

        print("Thank you for shopping!")
        break


    else:

        print("Invalid choice. Please try again.")

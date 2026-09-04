The Shopping Cart Management System is a Python-based application that allows users to manage products in a shopping cart and calculate the final bill. The program uses a menu-driven interface, where the user can select different operations until they choose to exit.

The system stores product details using dictionaries inside a Python list. Each product contains its name, price, and quantity.

Main Features
Add Product: Users can add a new product to the cart. If the product already exists, its quantity is updated.
Remove Product: Users can remove a specific product from the cart.
Change Quantity: Users can modify the quantity of an existing product. If the quantity is set to zero or below, the product is removed.
Display Cart: Shows all products along with their price, quantity, and total cost.
Apply Discount: Calculates a 10% discount on the total cart value.
Calculate Final Bill: Calculates the subtotal, discount, amount after discount, 18% GST, and the final payable amount.
Exit: Terminates the program with a thank-you message.
Calculation Formula
Product Total = Price × Quantity
Discount = Subtotal × 10%
Amount After Discount = Subtotal − Discount
GST = Amount After Discount × 18%
Final Bill = Amount After Discount + GST

This project demonstrates important Python concepts such as lists, dictionaries, loops, conditional statements, functions of arithmetic operations, user input, and menu-driven programming. It can be used as a basic model for developing a real-world shopping cart or billing system.

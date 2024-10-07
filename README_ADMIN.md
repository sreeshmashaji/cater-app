=>admin
   -config
      . database.py
   -routes
      . admin.py (register,login,view-users,reset-password)
      . restaurant.py(add-restaurants,view-restaurants,delete-restaurants,search-by-location)
   -schemas
      . admin_schema.py(all achemas for admin)
      . restaurant.py (all schemas for restaurants)

    - services
      . sms.py (sending otp to mobile number)

    - main.py (contains app instance ..it include routes of admin and restaurant)
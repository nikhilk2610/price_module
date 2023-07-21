#Pricing Module

- It Calculates Dynamic fare based on provided Pricing Configs.

#Getting Started
Follow these instructions to set up and run the project on your local machine.

#Prerequisites
Before running the app, you need to have the following installed:

Python (version 3.7 or higher)
Django (version 3.2 or higher)
Django REST Framework (version 3.12 or higher)
djangorestframework-simplejwt (version 4.8 or higher)


# Installation
Clone the repository or download the project files.
https://github.com/nikhilk2610/price_module.git

cd price_module

run "pip install -r requirements.txt"

#Database Setup
By default, the app uses the SQLite database. You can change the database settings in the settings.py file if needed.

#Run migrations to create the database tables.
python manage.py migrate

#Running the App
Use the following command to start the development server:
python manage.py runserver


The app will be accessible at http://127.0.0.1:8000/ or http://localhost:8000/.


#To obtain a token:
POST /api/token: Get a JWT token by providing valid credentials. This endpoint uses TokenObtainPairView.

#API Endpoints
The following API endpoints are available in this app:

#Pricing Config
- GET, POST /pricing_config: Get a list of pricing configurations or create a new pricing configuration.
 
  - GET, PUT, DELETE /pricing_config/<int:pk>: Retrieve, update, or delete a specific pricing configuration based on its primary key.
     Example Input for create/update
      {
      "distance_base_price": "80.00",
      "base_distance": "3",
      "day": 1,
      "distance_additional_price": "30.00",
      "time_multiplier_factor": "1,1.5",
      "waiting_charges": "5.00",
      "waiting_time_threshold": 3,
      "is_active": true
     }
  - 
- POST /calculate_price: Calculate the pricing dynamically based on the provided data.
  - Example Input
      {
      "distance_traveled": 20,
      "distance_traveled_each_hour": "10,10",
      "waiting_time": 10,
      "date": "2023-07-17"
      }

#Action Logs
The app also provides action logs to track changes made to pricing configurations.

GET /action_logs: Get a list of action logs containing changes made to pricing configurations.



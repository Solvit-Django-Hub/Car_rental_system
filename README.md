#  Car Rental System

A Django REST Framework-based Car Rental System that allows customers to view available cars, make rentals, manage profiles, make payments, and submit reviews.

##  Project Overview

The Car Rental System is a web-based REST API developed using Django and Django REST Framework.

The system is designed to manage:

- Users and user profiles
- Cars and car categories
- Car rentals
- Payments
- Customer reviews
- Authentication and authorization
- API access and documentation

##  Technologies Used

- Python
- Django
- Postgres


## 📂 Project Structure


car_rental_system/
│
├── accounts/
│   ├── models.py
│   ├── admin.py
│   ├── serializers.py
│   ├── views.py
│   └── ...
│
├── cars/
│   ├── models.py
│   ├── admin.py
│   ├── serializers.py
│   ├── views.py
│   └── ...
│
├── rentals/
│   ├── models.py
│   ├── admin.py
│   ├── serializers.py
│   ├── views.py
│   └── ...
│
├── car_rental_system/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md

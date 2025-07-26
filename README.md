# **ShareRoute – A Carpooling & Ride Sharing Platform**

## **Overview**  
**ShareRoute** is a Django-based web application designed to promote carpooling and reduce carbon emissions by allowing users to share rides. The platform connects drivers and passengers, enabling drivers to post rides and passengers to book available seats. The system also calculates the **estimated CO₂ saved per seat**, encouraging environmentally friendly travel.

---

## **Key Features**

### **For All Users (Guests & Registered)**
- **Index Page** – Search for available rides, view upcoming rides, and check ride details.  
- **Ride Details View** – View driver, vehicle, departure time, and CO₂ saved per seat.

### **For Registered Users**
- **User Authentication & Profile Management** –  
  Register, log in, edit profile details, upload profile pictures, and register as a driver.  

- **Vehicle Management for Drivers** –  
  Add, edit, and delete vehicles. Upload vehicle images and registration documents. EVs are marked with an **EV badge**.

- **Post & Manage Rides** –  
  Drivers can post rides by specifying:
  - Origin, destination, and departure time
  - Available seats and rate per seat
  - **Approximate distance (in km)** → System calculates **CO₂ saved per seat**  
  Drivers can also edit or delete their rides and view passenger bookings.

- **Book Rides (for Passengers)** –  
  View ride details, select seats, and see **real-time total cost calculation** before booking.

- **Booking History & Ride Details** –  
  Passengers can view their booking history and cancel upcoming bookings.  
  Drivers can view passenger bookings for their rides.

- **Password Reset** – Secure password reset with email support.

---

## **Tech Stack**
- **Backend:** Django 5.x, Python 3.x  
- **Frontend:** HTML, CSS, Bootstrap, JavaScript  
- **Database:** SQLite (default Django database)  
- **Authentication & Security:** Django’s built-in authentication system, CSRF protection, session-based cookies

---

## **Database Models**
The project uses four main models:

1. **UserProfile** – Extended user information, including profile picture, phone number, and driver registration.  
2. **Vehicle** – Stores vehicle details, images, and registration documents.  
3. **Ride** – Stores ride details, available seats, rate per seat, and **CO₂ saved per seat**.  
4. **Booking** – Stores passenger bookings and seat reservations.

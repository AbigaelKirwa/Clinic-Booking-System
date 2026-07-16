# Clinic-Booking-System

## System Design

### Overview

This project implements a RESTful appointment booking system for a small clinic with five doctors. Patients can view available appointment slots for a doctor, book appointments, cancel existing appointments, and reschedule appointments.

The system is intentionally designed with scalability in mind. Although the current requirements assume only five doctors and 30-minute appointment slots, the architecture allows additional doctors, authentication, notifications, and more advanced scheduling rules to be added with minimal changes.

---

# Architecture

The application follows a layered architecture to separate concerns.

```
REST API (FastAPI)

        │

Business Logic (Services)

        │

Repositories / ORM

        │

PostgreSQL
```

Each layer has a single responsibility:

* **API Layer** handles HTTP requests and responses.
* **Service Layer** contains business rules such as booking validation and availability calculations.
* **Repository Layer** manages database operations.
* **Database** stores persistent application data.

This separation makes the system easier to test, maintain, and extend.

---

# Core Models

## Doctor

Represents a doctor who accepts appointments.

Attributes:

* id
* name
* working_start_time
* working_end_time

Each doctor has configurable working hours from which appointment slots are generated.

---

## Patient

Represents a clinic patient.

Attributes:

* id
* full_name
* email
* phone_number

A patient may have many appointments.

---

## Appointment

Represents a booking between a patient and a doctor.

Attributes:

* id
* doctor_id
* patient_id
* start_time
* end_time
* status
* cancellation_reason
* created_at

Appointment Status:

* BOOKED
* CANCELLED

Cancelled appointments remain in the database for audit purposes, but no longer reserve a time slot.

---

# Slot Generation

Available slots are generated dynamically using the doctor's configured working hours.

For example:

Doctor working hours:

```
09:00 - 17:00
```

Generated slots:

```
09:00

09:30

10:00

...

16:30
```

Booked appointments are removed from this generated list before the response is returned.

### Why this approach?

Generating slots dynamically avoids storing thousands of unnecessary records while making working hours easy to change.

Trade-off:

Availability calculations require generating slots each time the endpoint is called. For a clinic of this size, this cost is negligible and greatly simplifies the data model.

---

# Booking Flow

Booking follows the sequence below:

1. Patient requests available slots.
2. System generates all valid slots.
3. Existing appointments are removed.
4. Patient selects a slot.
5. Booking request is validated.
6. Appointment is saved.
7. Updated availability reflects the booked slot.

---

# Validation Rules

The booking service validates that:

* the doctor exists
* the patient exists
* the appointment is in the future
* bookings cannot be made within one hour of the current time
* the appointment falls within the doctor's working hours
* appointments begin on a valid 30-minute boundary
* the slot has not already been booked

Validation failures return appropriate HTTP status codes together with meaningful error messages.

---

# Concurrency

Multiple patients may attempt to book the same appointment simultaneously.

To prevent duplicate bookings, the database enforces a unique constraint on:

```
(doctor_id, start_time)
```

Even if two booking requests arrive at the same time, only one transaction can succeed.

The application catches the resulting database integrity error and returns an HTTP 409 Conflict response.

---

# Cancellation

Cancelling an appointment changes its status to **CANCELLED** and records a cancellation reason.

The appointment remains stored for historical purposes.

Cancelled appointments are ignored when calculating availability, making the slot immediately bookable again.

Cancelling an already cancelled appointment returns an error.

---

# Rescheduling

Rescheduling is treated as an atomic operation.

The system:

1. validates the new slot
2. reserves the new slot
3. releases the old slot

These operations execute within a single database transaction.

This guarantees that a patient never loses an existing appointment if the new slot becomes unavailable during the rescheduling process.

Cancelled appointments cannot be rescheduled.

---

# Time Handling

All timestamps are stored in UTC within the database.

This avoids ambiguity across time zones and daylight saving changes.

User interfaces are responsible for displaying dates and times in the user's local timezone.

---

# Future Scalability

The current implementation satisfies the assignment requirements while allowing future enhancements, such as:

* JWT authentication
* Role-based access control
* Doctor leave management
* Holiday calendars
* Variable appointment durations
* Appointment reminders
* Email and SMS notifications
* Waitlists
* Multi-clinic support

---

# Assumptions

The following assumptions were made during implementation:

* Doctors work fixed daily hours.
* Appointment duration is always 30 minutes.
* Doctors cannot have overlapping appointments.
* Patients may have multiple future appointments.
* Existing appointments remain valid even if a doctor's working hours change later.
* The system stores cancelled appointments instead of deleting them.

---

## Soft Cancellation vs Deletion

Chosen:

Soft cancellation.

Advantages:

* Maintains appointment history.
* Supports auditing.
* Enables reporting.

Disadvantage:

* Queries must ignore cancelled appointments when calculating availability.

---

## Layered Architecture

Business logic is intentionally separated from API routes.

Advantages:

* Easier testing.
* Improved maintainability.
* Better separation of concerns.
* Simpler future expansion.

This structure keeps HTTP handling independent from the application's booking logic.


## Deployment & CI/CD

**Public URL:** `https://client-booking-system.fastapicloud.dev`

### Pipeline overview

This project uses **GitHub Actions** for continuous integration.

**On every pull request into `main`:**
* Checks out the repository
* Sets up Python 3.12
* Installs backend dependencies from `requirements.txt`
* Runs the backend test suite with `pytest`

The workflow is defined in `.github/workflows/ci.yml`. A PR should only be merged after these checks pass.

**Deployment branch:** `main`

After a PR is merged into `main`, the application is deployed to **FastAPI Cloud** (the hosted production environment). Feature branches such as `feature/dev`, `feature/project-setup`, and `feature/database-setup` were used during development for setup and incremental work; they feed into `main` through pull requests rather than deploying on their own.

---

## AI usage reflection

* **What AI was used for**
  * Refining API routes, services, and Pydantic schemas (doctors, availability, appointments)
  * Implementing booking rules (slot generation, validation, cancel, reschedule)
  * Debugging deployment issues (missing `fastapi[standard]`, `DATABASE_URL` on Cloud)
  * Tightening README / CI wording

* **One place AI improved the work**
  * **Prompt (paraphrased):** help implement `GET /doctors/{id}/availability` for 30-minute slots, then booking validation that only accepts those slots.
  * **What improved:** shared `slot_utils` so availability and booking use the same slot rules, which avoided mismatched “free” vs “bookable” times (e.g. rejecting `08:10–08:40`).

* **One place AI was wrong or incomplete**
  * Early booking code paths / suggestions treated conflicts mainly as duplicates, but inserts were also failing because `status` was never set to `booked`.
  * **How it was caught:** Cloud/local logs showed `status: None` on insert and 409 responses that were not true “slot already taken” cases; fixing status and validation clarified real conflicts vs bad payloads.

* **Two decisions made without AI**
  * **Soft cancellation** (keep the row, set status to `cancelled`) instead of deleting appointments — needed for history/audit and so cancelled slots become bookable again without losing records.
  * **Layered architecture** (routes → services → models) — keeps HTTP concerns out of booking rules so validation and tests stay maintainable as features grow.


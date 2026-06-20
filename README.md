# CooperAcao

**Voluntary Blood Donation Network**

A web platform that connects voluntary blood donors with local blood banks and hospitals in real time.

Developed as a Capstone Project for the **Systems Analysis and Development Program** at **Senac College**.

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Senac](https://img.shields.io/badge/Institution-Senac%20College-blue)](https://www.senac.br/)
[![LGPD](https://img.shields.io/badge/Compliance-LGPD%20Ready-blueviolet)](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm)

## Project Overview

CooperAcao bridges the gap between voluntary blood donors and blood banks.

Blood centers can post urgent blood type shortages, while donors receive smart notifications when their specific blood type is needed nearby.

## Key Features

- **Urgent Demand Feed:** Real-time dashboard showing blood supply levels.
- **Smart Match Scheduling:** Donation appointments based on proximity and hospital demand.
- **Privacy-First Profiles:** Users control their medical eligibility data and shared history.

## LGPD & Data Privacy

The platform handles sensitive personal data related to health and medical history.

### Implemented Privacy Standards

- **Explicit Consent:** Blood type and availability data are used only with donor consent.
- **Data Minimization:** Sensitive screening answers are not permanently stored unless required.
- **User Rights Panel:** Users can access, correct, or delete their registered data.
- **Consent Revocation:** Users can revoke consent and request account deletion.
- **Security:** Passwords and sensitive matching fields are hashed with bcrypt.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | React.js, Tailwind CSS, TypeScript |
| Backend | Node.js, Fastify, Prisma ORM |
| Database | PostgreSQL |
| Testing | Vitest |

## Core API Endpoints

| Method | Endpoint | Description | LGPD Scope |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | Registers a new user account | Consent collection |
| POST | `/api/donors/schedule` | Records a donation appointment | Temporary sensitive data |
| GET | `/api/privacy/export` | Downloads user data as JSON | Right to access |
| DELETE | `/api/privacy/purge` | Deletes account and records | Right to erasure |

## Future Improvements

- **Deep Sleep Cycle:** Optimize ESP32 power consumption with solar and battery support.
- **Machine Learning:** Predict depletion rates using regression models.
- **Enclosure:** Design a 3D printed IP65 waterproof housing.

## Authors & Project Team

| Name | Role |
| --- | --- |
| Felipe Calado de Sousa | Backend & Privacy Architecture Specialist |
| Pedro Reynaldo Maia Vasconcelos | Frontend Developer |
| Otto Notaro | UI/UX & Product Owner |

**Academic Advisor / Professor:** Prof. ____________

**Tech English Course Professor:** Prof. Leonardo Trevas

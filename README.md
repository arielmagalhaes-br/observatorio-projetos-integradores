# Conecta PI

**Academic Project Observatory**

A web platform that centralizes, organizes, and showcases Capstone Projects from Senac Pernambuco.

Conecta PI connects students, teachers, administrators, and partner organizations through academic innovation and real-world demands.

[![Django](https://img.shields.io/badge/Framework-Django-green)](https://www.djangoproject.com/)
[![Senac](https://img.shields.io/badge/Institution-Senac%20Pernambuco-blue)](https://www.senac.br/)
[![SDG](https://img.shields.io/badge/Focus-SDG%20Projects-blueviolet)](https://sdgs.un.org/goals)

## Project Overview

Conecta PI was designed to prevent academic projects from being forgotten after the semester.

The platform works as a digital observatory where students publish projects, teachers curate submissions, and partner organizations discover solutions for real needs.

## Key Features

- **Project Showcase:** Public gallery with approved academic projects.
- **Student Dashboard:** Project registration, editing, images, documents, and useful links.
- **Teacher Curation:** Review workflow with approval, feedback, and adjustment requests.
- **Partner Demands:** Companies and NGOs can register real operational needs.
- **Matchmaking Panel:** Connects partner demands with academic projects.
- **Metrics Dashboard:** Tracks projects, pending reviews, demands, and SDG indicators.

## LGPD & Data Privacy

The platform handles user accounts, profile data, project files, images, and partner organization information.

### Implemented Privacy Standards

- **Role-Based Access:** Different permissions for students, teachers, administrators, and partners.
- **Authentication:** Protected pages require login before accessing private information.
- **Data Minimization:** Project and profile forms collect only relevant academic information.
- **Curated Publication:** Projects appear in the public showcase only after approval.
- **Controlled Editing:** Students can edit only their own drafts or projects returned for adjustments.

## Tech Stack

| Layer | Technologies |
| --- | --- |
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Django |
| Database | SQLite |
| Media Handling | Pillow |
| Architecture | Django Templates, Models, Views, Migrations |

## Core Platform Routes

| Route | Description | Main User |
| --- | --- | --- |
| `/` | Gateway for choosing the user profile | Public |
| `/login/` | User authentication | All users |
| `/home/` | Student dashboard | Students |
| `/meus-projetos/` | Student project management | Students |
| `/novo-projeto/` | New project submission | Students |
| `/curadoria/` | Project review queue | Teachers |
| `/parcerias/` | Partner demands panel | Teachers |
| `/matchmaking/` | Demand and project matching | Teachers |
| `/vitrine/` | Public showcase of approved projects | Public |

## Future Improvements

- **Smart Recommendations:** Suggest projects for partner demands automatically.
- **Notification System:** Alert students when teachers request adjustments.
- **Advanced Analytics:** Export dashboards with project, course, semester, and SDG data.
- **Partner Portal:** Expand demand registration and tracking for companies and NGOs.

## Authors & Project Team

| Role | Responsibility |
| --- | --- |
| Students | Project development and documentation |
| Teachers | Academic curation and feedback |
| Partner Organizations | Real demands and validation |
| Administrators | Platform management and continuity |

**Academic Institution:** Senac Pernambuco

**Project Type:** Capstone Project / Projeto Integrador

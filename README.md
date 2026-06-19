# Conecta PI

**Academic projects should not be forgotten after the semester.**

Conecta PI is a web platform that organizes, showcases, and connects Capstone Projects from Senac Pernambuco with real demands from companies and NGOs.

## Presentation Pitch

### 1. The Problem

- Many academic projects end up forgotten in archives.
- Small businesses and NGOs struggle to find ready-to-use solutions.
- Student talent and innovation often go unnoticed.

### 2. The Solution

- A digital observatory for Capstone Projects.
- A showcase for academic innovation.
- A bridge between students, teachers, companies, and NGOs.

### 3. Who Uses It

| User | Main Goal |
| --- | --- |
| Students | Register, manage, and publish their projects. |
| Teachers | Review, approve, and curate projects. |
| Partner Organizations | Find solutions and submit real demands. |
| Administrators | Manage users, metrics, and platform continuity. |

### 4. Key Features

- Project registration with documentation, images, links, and technologies.
- Public showcase with search and filters.
- Teacher curation and approval workflow.
- Partner demand panel for companies and NGOs.
- Dashboards with project metrics and SDG indicators.
- Matchmaking between real demands and academic projects.

### 5. Market Need

- 28.7% rated the platform as highly important.
- 71.3% showed interest in using it during the semester.
- The demand exists, but the connection is still inefficient.

### 6. Benchmarking

| Platform | Limitation |
| --- | --- |
| GitHub | No academic curation or project showcase. |
| Devpost | No connection with classes or local demands. |
| DSpace | Focused on repositories, not active matchmaking. |

### 7. Differentiators

- Specific filters for each user experience.
- Structured demand management for companies and NGOs.
- Academic and industry approval seal.
- Focus on Senac Pernambuco's project ecosystem.

### 8. Technologies Used

- Python
- Django
- SQLite
- HTML5
- CSS3
- JavaScript
- Pillow

### 9. Demo Flow

1. Log in as a student.
2. Register a new project.
3. Send it to teacher review.
4. Approve the project through curation.
5. View it in the public showcase.
6. Match it with partner demands.

## Short Speaking Script

- **Opening:** Conecta PI gives more visibility and real impact to academic projects.
- **Problem:** Many good projects are finished, delivered, and then forgotten.
- **Solution:** The platform connects student projects with real needs from companies and NGOs.
- **Users:** Students publish, teachers curate, partners discover, and administrators monitor.
- **Value:** Conecta PI transforms academic production into practical innovation.
- **Closing:** The goal is to make student projects visible, useful, and connected to the real world.

## Run Locally

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

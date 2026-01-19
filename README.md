# Book Finder

A web-based application for tracking books and their locations at local stores. Helps readers find books at nearby bookstores, libraries, and retailers, while allowing store owners to manage their inventory online.

## Features

### For Readers
- Search for books by ISBN, title, or author
- View real-time inventory and pricing information
- Interactive map showing store locations
- Location-based search to find nearby stores
- Detailed book and store information

### For Bookstores
- Easy store registration and profile management
- Online inventory management
- Add, edit, and remove books from inventory
- Track quantity, pricing, and book condition
- Make inventory discoverable to local customers

## Technology Stack

- **Backend**: Python Flask
- **Database**: MongoDB with geospatial indexing
- **Frontend**: HTML, CSS, JavaScript
- **Maps**: Leaflet.js with OpenStreetMap
- **Authentication**: Flask-Login with bcrypt
- **Containerization**: Docker and Docker Compose
- **Package Management**: UV

## Architecture

The application uses a modular architecture with clear separation of concerns:

```
book-finder/
├── app/
│   ├── models/          # Data models (Store, Book, Inventory, SearchIndex)
│   ├── routes/          # Route blueprints (main, store, book, search)
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JS, images
│   ├── utils/           # Utilities (database manager)
│   └── __init__.py      # Flask app factory
├── config/              # Configuration files
├── tests/               # Test files
├── docker-compose.yml   # Container orchestration
├── Dockerfile           # Flask app container
├── pyproject.toml       # Python dependencies
└── run.py               # Application entry point
```

## Data Models

- **Store**: Store information including name, location, hours, contact details, and authentication credentials
- **Book**: Book details including ISBN, title, author, and cover image
- **Inventory**: Links stores to books with quantity, price, and condition information
- **SearchIndex**: Tokenized search index for efficient book searching

## Prerequisites

- Docker and Docker Compose installed on your system
- OR Python 3.10+ and MongoDB (for local development)

## Getting Started

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd book-finder
```

2. Create a `.env` file (optional, uses defaults if not provided):
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and start the containers:
```bash
docker-compose up --build
```

4. Access the application at `http://localhost:5000`

### Local Development

1. Install UV package manager:
```bash
pip install uv
```

2. Install dependencies:
```bash
uv pip install -r pyproject.toml
```

3. Start MongoDB:
```bash
# Using Docker
docker run -d -p 27017:27017 --name mongodb mongo:7.0

# OR use your local MongoDB installation
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Run the application:
```bash
python run.py
```

6. Access the application at `http://localhost:5000`

## Usage

### For Store Owners

1. **Register Your Store**
   - Navigate to "Register Store"
   - Fill in store details (name, address, coordinates, hours, contact)
   - Create your account

2. **Manage Inventory**
   - Log in to your dashboard
   - Click "Add New Book" to add books to your inventory
   - Enter ISBN, title, author, quantity, price, and condition
   - Edit or delete inventory items as needed

3. **Update Profile**
   - Access your profile from the dashboard
   - Update store information as needed

### For Readers

1. **Search for Books**
   - Enter ISBN, title, or author in the search box
   - Optionally enable location-based search
   - Select search type (All, ISBN, Title, Author)

2. **View Results**
   - Browse search results
   - See which stores have the book in stock
   - View pricing, condition, and availability
   - Click on map markers to see store details

## API Endpoints

### Search
- `GET /search/?q=<query>&type=<type>&lat=<lat>&lng=<lng>` - Search for books
- `GET /search/autocomplete?q=<query>` - Autocomplete suggestions

### Store Management
- `GET /store/register` - Store registration page
- `POST /store/register` - Create new store account
- `GET /store/login` - Store login page
- `POST /store/login` - Authenticate store
- `GET /store/dashboard` - Store dashboard (requires login)
- `GET /store/profile` - Store profile management (requires login)
- `POST /store/profile` - Update store profile (requires login)
- `GET /store/logout` - Logout

### Book Management
- `GET /books/add` - Add book page (requires login)
- `POST /books/add` - Add book to inventory (requires login)
- `GET /books/edit/<isbn>` - Edit inventory page (requires login)
- `POST /books/edit/<isbn>` - Update inventory (requires login)
- `POST /books/delete/<isbn>` - Delete from inventory (requires login)
- `GET /books/<isbn>` - View book details

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| FLASK_ENV | Flask environment | development |
| SECRET_KEY | Flask secret key | dev-secret-key-change-in-production |
| MONGO_URI | MongoDB connection URI | mongodb://mongodb:27017/ |
| MONGO_DB_NAME | Database name | bookfinder |
| DEBUG | Debug mode | True |
| HOST | Server host | 0.0.0.0 |
| PORT | Server port | 5000 |

## Database Indexes

The application automatically creates the following MongoDB indexes for optimal performance:

- **stores**: Geospatial index on location, unique index on email
- **books**: Unique index on ISBN
- **inventory**: Composite unique index on (store_id, isbn)
- **search_index**: Indexes on ISBN, title_tokens, and author_tokens

## Future Enhancements

- Redis cache integration for improved performance
- Nginx reverse proxy with TLS/SSL support
- Advanced search filters (price range, condition, distance)
- Barcode scanning for easier book entry
- Email notifications for inventory updates
- User reviews and ratings
- Mobile-responsive design improvements
- Cloud deployment configuration
- API rate limiting
- Admin dashboard

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black app/ tests/
```

### Linting
```bash
flake8 app/ tests/
```

## Contributing

This is a minimum viable product (MVP) designed for easy extension. Contributions are welcome!

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions, please open an issue on the project repository.

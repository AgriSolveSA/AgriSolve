
# AgriSolve
agrisolve-server/
│
├── src/                    # All actual backend logic lives here
│
│   ├── controllers/        # Functions that run when a route is called
│   │   └── farmController.js  # Handles farm-related requests (e.g. create farm, update farm)
│
│   ├── routes/             # Defines URLs like /api/farms
│   │   └── farmRoutes.js     # Maps HTTP requests to farmController functions
│
│   ├── models/             # Data structure and validation for database entries
│   │   └── farmModel.js      # Defines how a "farm" is structured in the database
│
│   ├── services/           # Business logic & integrations (e.g., WhatsApp API)
│   │   └── whatsappService.js # A service for sending farm alerts via WhatsApp
│
│   ├── db/                 # DB configuration, connection setup
│   │   └── index.js          # Initializes your connection to PostgreSQL, MySQL, etc.
│
│   ├── middleware/         # Code that runs *before* or *after* a request
│   │   └── errorHandler.js   # Custom error catching
│
│   └── index.js            # Main entry point of the backend server
│
├── .env                    # Secrets like DB passwords, API keys
├── package.json            # Lists dependencies & scripts (like "start server")
└── README.md               # Notes for developers on how to run/setup the project

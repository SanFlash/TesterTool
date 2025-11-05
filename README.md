# Flask Site Tester

Flask Site Tester is a web application that allows users to input a website URL, analyze its structure, and auto-generate a detailed test case table. This project is built using Flask and leverages various libraries to fetch, parse, and analyze web content.

## Features

- Input a website URL for analysis.
- Fetch and parse the HTML content of the provided URL.
- Generate test cases based on the structure of the webpage.
- Display results in a user-friendly format.

## Project Structure

```
flask-site-tester
├── src
│   ├── app.py                  # Entry point of the Flask application
│   ├── analyzer
│   │   ├── __init__.py         # Marks the analyzer directory as a package
│   │   ├── crawler.py           # Fetches webpage content
│   │   ├── parser.py            # Parses HTML content
│   │   └── test_generator.py     # Generates test cases
│   ├── templates
│   │   ├── base.html            # Base HTML template
│   │   ├── index.html           # Input form for URL
│   │   └── results.html         # Displays analysis results
│   └── static
│       ├── css
│       │   └── styles.css       # CSS styles for the application
│       └── js
│           └── main.js          # JavaScript for client-side interactions
├── tests
│   ├── test_analyzer.py         # Unit tests for the analyzer module
│   └── test_app.py              # Unit tests for the Flask application
├── requirements.txt              # Project dependencies
├── Dockerfile                    # Instructions for building a Docker image
├── .gitignore                    # Files to ignore in version control
└── README.md                     # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-site-tester
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the application:
   ```
   python src/app.py
   ```

4. Open your web browser and navigate to `http://127.0.0.1:5000` to access the application.

## Usage

- Enter a valid website URL in the input form and submit.
- The application will analyze the structure of the website and generate a detailed test case table.
- Review the results displayed on the results page.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.
 
## Optional authentication and local fallback

This project supports Supabase Auth (recommended for production). If you set `SUPABASE_URL` and `SUPABASE_KEY` in your environment (or `.env`), the app will use Supabase for signup/login/password resets.

If you do not provide Supabase credentials, the app will automatically use a local SQLite fallback for authentication (development only). The local DB file is created at `data/auth.db`. The fallback supports signup, login, forgot-password (a development reset link is shown), and password reset via a token.

Important: The local fallback is intended for convenience and testing only. Use Supabase (or another managed auth provider) for production deployments.
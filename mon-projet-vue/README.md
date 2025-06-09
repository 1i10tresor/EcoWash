# EcoWash Balancing Calculator

A web application for calculating EcoAdd additives for solvent rebalancing in industrial coating systems.

## Project Structure

```
├── main.py                 # Main Flask backend application
├── mainEcoWash.py         # Alternative backend implementation
├── mon-projet-vue/        # Vue.js frontend application
│   ├── src/
│   │   ├── App.vue        # Main application component
│   │   ├── components/
│   │   │   └── CalculatorForm.vue  # Calculator form component
│   │   └── main.js        # Vue application entry point
│   └── package.json       # Frontend dependencies
├── recette/               # Excel recipe files
│   ├── EcoWash - 1B.xlsx
│   ├── EcoWash - base.xlsx
│   └── EcoWash - bis.xlsx
└── calculations.db        # SQLite database for storing calculations

```

## Features

- **Multi-language support**: French, English, and German
- **Solvent calculation**: Handles both 3-component and 4-component solvent systems
- **Email notifications**: Send calculation results via email
- **Recipe management**: Load different EcoWash formulations from Excel files
- **Calculation history**: Store and track calculations in SQLite database

## Backend (Flask)

### Dependencies
- Flask
- Flask-CORS
- NumPy
- Pandas
- yagmail
- sqlite3

### Key Functions
- `etape_1()`: Solves system of equations for component concentrations
- `etape_2()`: Determines which component is in excess
- `etape_3()`: Calculates required additive quantities
- `solvant_initial()`: Loads initial solvent data from Excel
- `EcoAdds()`: Extracts EcoAdd additive data from Excel

### API Endpoints
- `POST /calculate`: Perform solvent rebalancing calculations
- `GET /recette`: Get list of available recipe files
- `POST /send_mail`: Send calculation results via email

## Frontend (Vue.js)

### Dependencies
- Vue 3
- Axios
- Vite

### Components
- `App.vue`: Main application with language switching and layout
- `CalculatorForm.vue`: Form for inputting measurement data and displaying results

### Features
- Responsive design
- Real-time form validation
- Error handling and user feedback
- Email integration for results sharing

## Installation

### Backend Setup
1. Install Python dependencies:
   ```bash
   pip install flask flask-cors numpy pandas yagmail
   ```

2. Run the Flask application:
   ```bash
   python main.py
   ```

### Frontend Setup
1. Navigate to the Vue project:
   ```bash
   cd mon-projet-vue
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Usage

1. Select an EcoWash model from the dropdown
2. Choose measurement type (IR or BRIX)
3. Enter density and refraction values
4. Click "Calculate" to get additive recommendations
5. Optionally send results via email

## Database Schema

The application uses SQLite to store calculation history:

```sql
CREATE TABLE calculations (
    id TEXT PRIMARY KEY,
    model TEXT,
    measurement_type TEXT,
    lot_number INTEGER,
    density REAL,
    refraction REAL,
    result TEXT,
    calculation_date TIMESTAMP,
    email TEXT,
    sent_email BOOLEAN DEFAULT FALSE
);
```

## Configuration

### Email Configuration
Update the email credentials in the `send_mail()` function:
```python
yag = yagmail.SMTP('your-email@gmail.com', 'your-app-password')
```

### Excel Recipe Files
Place Excel files in the `recette/` directory with the following structure:
- `Composant`: Component name
- `concL`: Concentration
- `density`: Density value
- `IR`: Refractive index
- `ComposantsEcoAdd`: EcoAdd component names
- `ecoAddH`, `ecoAddA`, `ecoAddS`: EcoAdd concentrations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is proprietary software developed for Spring Coating Systems.

## Contact

For technical support or questions:
- Email: ecowash.balancing@spring-coating.com
- Phone: 07 60 11 07 85

## Company Information

**Spring Coating Systems**  
18 rue de la Fabrique  
68530 BUHL  
Phone: 03 89 83 06 82

Spring Coating Systems is a formulator and manufacturer of inks, varnishes, adhesives, and paints for industrial applications and packaging printing.
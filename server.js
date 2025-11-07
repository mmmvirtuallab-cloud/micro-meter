const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Data storage file
const DATA_FILE = path.join(__dirname, 'data', 'measurements.json');

// Ensure data directory exists
if (!fs.existsSync(path.dirname(DATA_FILE))) {
    fs.mkdirSync(path.dirname(DATA_FILE), { recursive: true });
}

// Initialize data file if it doesn't exist
if (!fs.existsSync(DATA_FILE)) {
    const initialData = {
        measurements: [],
        problems: [],
        statistics: {
            totalMeasurements: 0,
            averageAccuracy: 0,
            lastUpdated: new Date().toISOString()
        }
    };
    fs.writeFileSync(DATA_FILE, JSON.stringify(initialData, null, 2));
}

// Helper function to read data
const readData = () => {
    try {
        const data = fs.readFileSync(DATA_FILE, 'utf8');
        return JSON.parse(data);
    } catch (error) {
        console.error('Error reading data file:', error);
        return { measurements: [], problems: [], statistics: {} };
    }
};

// Helper function to write data
const writeData = (data) => {
    try {
        fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2));
        return true;
    } catch (error) {
        console.error('Error writing data file:', error);
        return false;
    }
};

// Routes

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({ 
        status: 'OK', 
        message: 'Micrometer Virtual Laboratory Backend is running!',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// Get all measurements
app.get('/api/measurements', (req, res) => {
    try {
        const data = readData();
        res.json({
            success: true,
            data: data.measurements,
            count: data.measurements.length
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to fetch measurements',
            message: error.message
        });
    }
});

// Save a new measurement
app.post('/api/measurements', (req, res) => {
    try {
        const data = readData();
        const measurement = {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            sessionId: req.body.sessionId || 'anonymous',
            ...req.body
        };

        data.measurements.push(measurement);
        
        // Update statistics
        data.statistics.totalMeasurements = data.measurements.length;
        data.statistics.lastUpdated = new Date().toISOString();
        
        if (writeData(data)) {
            res.json({
                success: true,
                data: measurement,
                message: 'Measurement saved successfully'
            });
        } else {
            throw new Error('Failed to save measurement');
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to save measurement',
            message: error.message
        });
    }
});

// Generate random problem
app.get('/api/problems/generate', (req, res) => {
    try {
        const objectTypes = ['rectangle', 'circle'];
        const msdValues = [0.5, 1.0, 1.5, 2.0];
        const csdCounts = [25, 50, 75, 100];
        
        const problem = {
            id: Date.now().toString(),
            timestamp: new Date().toISOString(),
            objectType: objectTypes[Math.floor(Math.random() * objectTypes.length)],
            zeroError: parseFloat((Math.random() - 0.5).toFixed(3)),
            msdValue: msdValues[Math.floor(Math.random() * msdValues.length)],
            csdCount: csdCounts[Math.floor(Math.random() * csdCounts.length)],
            difficulty: Math.floor(Math.random() * 3) + 1 // 1-3
        };

        // Add dimensions based on object type
        if (problem.objectType === 'rectangle') {
            problem.dimensions = {
                width: parseFloat((5 + Math.random() * 20).toFixed(1)),
                height: parseFloat((50 + Math.random() * 100).toFixed(0))
            };
        } else {
            problem.dimensions = {
                diameter: parseFloat((5 + Math.random() * 20).toFixed(1))
            };
        }
        
        // Save to problems array
        const data = readData();
        data.problems.push(problem);
        writeData(data);
        
        res.json({
            success: true,
            data: problem,
            message: 'Problem generated successfully'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to generate problem',
            message: error.message
        });
    }
});

// Get measurement statistics
app.get('/api/statistics', (req, res) => {
    try {
        const data = readData();
        const measurements = data.measurements;
        
        const stats = {
            totalMeasurements: measurements.length,
            totalProblems: data.problems.length,
            averageAccuracy: measurements.length > 0 ? 
                parseFloat((measurements.reduce((sum, m) => sum + (m.accuracy || 0), 0) / measurements.length).toFixed(2)) : 0,
            recentMeasurements: measurements.slice(-10),
            lastUpdated: data.statistics.lastUpdated || new Date().toISOString(),
            measurementsByDay: {},
            accuracyDistribution: {
                excellent: 0,  // >95%
                good: 0,       // 85-95%
                fair: 0,       // 75-85%
                poor: 0        // <75%
            }
        };

        // Calculate accuracy distribution
        measurements.forEach(m => {
            const accuracy = m.accuracy || 0;
            if (accuracy > 95) stats.accuracyDistribution.excellent++;
            else if (accuracy >= 85) stats.accuracyDistribution.good++;
            else if (accuracy >= 75) stats.accuracyDistribution.fair++;
            else stats.accuracyDistribution.poor++;
        });
        
        res.json({
            success: true,
            data: stats
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to fetch statistics',
            message: error.message
        });
    }
});

// Delete a measurement
app.delete('/api/measurements/:id', (req, res) => {
    try {
        const data = readData();
        const measurementId = req.params.id;
        const initialLength = data.measurements.length;
        
        data.measurements = data.measurements.filter(m => m.id !== measurementId);
        
        if (data.measurements.length < initialLength) {
            data.statistics.totalMeasurements = data.measurements.length;
            data.statistics.lastUpdated = new Date().toISOString();
            
            if (writeData(data)) {
                res.json({
                    success: true,
                    message: 'Measurement deleted successfully'
                });
            } else {
                throw new Error('Failed to save updated data');
            }
        } else {
            res.status(404).json({
                success: false,
                error: 'Measurement not found'
            });
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to delete measurement',
            message: error.message
        });
    }
});

// Get all problems
app.get('/api/problems', (req, res) => {
    try {
        const data = readData();
        res.json({
            success: true,
            data: data.problems,
            count: data.problems.length
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to fetch problems',
            message: error.message
        });
    }
});

// Clear all data (for development/testing)
app.delete('/api/data/clear', (req, res) => {
    try {
        const initialData = {
            measurements: [],
            problems: [],
            statistics: {
                totalMeasurements: 0,
                averageAccuracy: 0,
                lastUpdated: new Date().toISOString()
            }
        };
        
        if (writeData(initialData)) {
            res.json({
                success: true,
                message: 'All data cleared successfully'
            });
        } else {
            throw new Error('Failed to clear data');
        }
    } catch (error) {
        res.status(500).json({
            success: false,
            error: 'Failed to clear data',
            message: error.message
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err.stack);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'Something went wrong!'
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: 'Route not found',
        message: `Cannot ${req.method} ${req.path}`
    });
});

// Start server
app.listen(PORT, () => {
    console.log('🚀 Micrometer Virtual Laboratory Backend Server Started!');
    console.log(`📍 Server running on: http://localhost:${PORT}`);
    console.log(`📊 Health Check: http://localhost:${PORT}/api/health`);
    console.log(`🔬 API Endpoints Available:`);
    console.log(`   GET    /api/health - Server health check`);
    console.log(`   GET    /api/measurements - Get all measurements`);
    console.log(`   POST   /api/measurements - Save new measurement`);
    console.log(`   DELETE /api/measurements/:id - Delete measurement`);
    console.log(`   GET    /api/problems - Get all problems`);
    console.log(`   GET    /api/problems/generate - Generate random problem`);
    console.log(`   GET    /api/statistics - Get measurement statistics`);
    console.log(`   DELETE /api/data/clear - Clear all data (dev only)`);
    console.log('=' * 60);
});

module.exports = app;
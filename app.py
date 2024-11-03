from flask import Flask, render_template, request, url_for
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use the 'Agg' backend for non-GUI rendering
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os
import io
import base64

app = Flask(__name__)

def create_directory(path='static'):
    if not os.path.exists(path):
        os.makedirs(path)

def simulate_data(num_points, mean, variance, simulations):
    rng = np.random.default_rng()
    # Generate X as a uniform random variable between 0 and 1
    x_values = rng.random(num_points)
    # Generate Y with normally distributed noise
    y_values = mean + np.sqrt(variance) * rng.standard_normal(num_points)
    return x_values, y_values

def fit_regression(x, y):
    model = LinearRegression()
    model.fit(x.reshape(-1, 1), y)
    return model.coef_[0], model.intercept_

def generate_scatter_plot(x, y, slope, intercept, filename='static/scatter_plot.png'):
    plt.figure()
    plt.scatter(x, y, color='blue', label='Data points')
    plt.plot(x, slope * x + intercept, color='red', label=f'Regression: Y = {slope:.2f}X + {intercept:.2f}')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.legend()
    plt.savefig(filename)
    plt.close()
    return filename

def simulate_and_plot_distributions(x_values, num_points, mean, variance, simulations, original_slope, original_intercept, filename='static/distribution_plot.png'):
    rng = np.random.default_rng()
    slopes, intercepts = [], []
    for _ in range(simulations):
        y_sim = mean + np.sqrt(variance) * rng.standard_normal(num_points)
        slope, intercept = fit_regression(x_values, y_sim)
        slopes.append(slope)
        intercepts.append(intercept)

    plt.figure()
    plt.hist(slopes, bins=30, alpha=0.5, label='Slopes')
    plt.axvline(original_slope, color='red', linestyle='--', linewidth=1, label='Original Slope')
    plt.hist(intercepts, bins=30, alpha=0.5, label='Intercepts')
    plt.axvline(original_intercept, color='blue', linestyle='--', linewidth=1, label='Original Intercept')
    plt.legend()
    plt.savefig(filename)
    plt.close()
    slope_extreme = np.mean(np.abs(slopes) > np.abs(original_slope))
    intercept_extreme = np.mean(np.abs(intercepts) > np.abs(original_intercept))
    return filename, slope_extreme, intercept_extreme


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        N = int(request.form['N'])
        mu = float(request.form['mu'])
        sigma2 = float(request.form['sigma2'])
        S = int(request.form['S'])

        create_directory()
        x_values, y_values = simulate_data(N, mu, sigma2, S)
        slope, intercept = fit_regression(x_values, y_values)

        scatter_plot = generate_scatter_plot(x_values, y_values, slope, intercept)
        dist_plot, slope_extreme, intercept_extreme = simulate_and_plot_distributions(
            x_values, N, mu, sigma2, S, slope, intercept)
        
        slope_extreme = f"{slope_extreme:.3f}"
        intercept_extreme = f"{intercept_extreme:.3f}"

        return render_template('index.html', plot1=scatter_plot, plot2=dist_plot, slope_extreme=slope_extreme, intercept_extreme=intercept_extreme)
    
    return render_template('index.html', plot1=None, plot2=None)


if __name__ == '__main__':
    app.run(debug=True)

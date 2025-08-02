from flask import Flask, render_template, request
import pandas as pd
import os
from arima_utils import segment_customers, churnForecast
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

app = Flask(__name__)
UPLOAD_FOLDER = 'static/plots'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['csv_file']
        if not file:
            return 'No file uploaded.'
        
        df = pd.read_csv(file)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)

        segmented_df = segment_customers(df)
        plt.figure(figsize=(10, 6))
        sns.countplot(x='Customer Segment', data=segmented_df, palette='Set2')
        plt.title('Customer Segments Count')
        plt.xticks(rotation=45)
        plt.tight_layout()
        segment_plot_filename = 'segment_count.png'
        segment_plot_path = os.path.join(app.config['UPLOAD_FOLDER'], segment_plot_filename)
        plt.savefig(segment_plot_path)
        plt.close()
        plot_paths = []
        plot_paths.append(("Count Plot",segment_plot_filename))
        for segment in segmented_df['Customer Segment'].unique():
            seg_data = segmented_df[segmented_df['Customer Segment'] == segment]
            full_path = churnForecast(seg_data, segment, app.config['UPLOAD_FOLDER'])
            filename_only = os.path.basename(full_path)
            plot_paths.append((segment, filename_only))


        return render_template('results.html', plots=plot_paths)
    return render_template('index.html')
if __name__ == '__main__':
    app.run(debug=True)
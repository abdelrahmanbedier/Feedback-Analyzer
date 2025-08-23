import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const SentimentPieChart = ({ stats }) => {
  // Don't render the chart if there's no data
  if (!stats || stats.total_count === 0) {
    return null;
  }

  const data = {
    labels: ['Positive', 'Neutral', 'Negative'],
    datasets: [
      {
        label: 'Feedback Count',
        data: [stats.positive_count, stats.neutral_count, stats.negative_count],
        backgroundColor: [
          'rgba(75, 192, 192, 0.7)',  // Teal for Positive
          'rgba(201, 203, 207, 0.7)', // Gray for Neutral
          'rgba(255, 99, 132, 0.7)',   // Red for Negative
        ],
        borderColor: [
          'rgba(75, 192, 192, 1)',
          'rgba(201, 203, 207, 1)',
          'rgba(255, 99, 132, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };

  return (
    <div className="chart-container">
      <Pie data={data} options={options} />
    </div>
  );
};

export default SentimentPieChart;
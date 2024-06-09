<template>
  <div class="history">
    <h2>历史测评结果</h2>
    <div v-if="!selectedResult">
      <ul>
        <li v-for="result in results" :key="result.id">
          <p>日期: {{ new Date(result.date_time).toLocaleString() }}</p>
          <button @click="viewResult(result)">查看结果</button>
        </li>
      </ul>
    </div>
    <div v-else>
      <h3>评估结果</h3>
      <p>日期: {{ new Date(selectedResult.date_time).toLocaleString() }}</p>
      <p>总分: {{ selectedResult.total_score }}/100</p>
      <div v-for="(score, dimension) in parsedDimensionScores" :key="dimension">
        <p>{{ dimension }}: {{ score === 'NA' ? '不适用' : score.toFixed(2) }}</p>
      </div>
      <canvas id="scoreChart"></canvas>
      <button @click="backToList">返回列表</button>
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
// eslint-disable-next-line
import { nextTick } from 'vue';

// Register Chart.js components
Chart.register(...registerables);

export default {
  name: 'EvaluationHistory',
  data() {
    return {
      results: [],
      selectedResult: null
    };
  },
  computed: {
    parsedDimensionScores() {
      if (this.selectedResult) {
        return JSON.parse(this.selectedResult.dimension_scores);
      }
      return {};
    }
  },
  created() {
    fetch('http://localhost:5000/evaluations')
      .then(response => response.json())
      .then(data => {
        this.results = data;
      })
      .catch(error => {
        console.error('Error fetching evaluation results:', error);
      });
  },
  methods: {
    viewResult(result) {
      this.selectedResult = result;
      // eslint-disable-next-line
      this.$nextTick(() => {
        this.renderChart();
      });
    },
    backToList() {
      this.selectedResult = null;
    },
    renderChart() {
      const ctx = document.getElementById('scoreChart').getContext('2d');
      const labels = Object.keys(this.parsedDimensionScores).filter(dimension => this.parsedDimensionScores[dimension] !== 'NA');
      const data = Object.values(this.parsedDimensionScores).filter(score => score !== 'NA');

      new Chart(ctx, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: '合规维度得分',
            data,
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      });
    }
  }
};
</script>

<style scoped>
.history {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f9f9f9;
}
h2, h3, p {
  text-align: center;
}
button {
  display: block;
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  font-size: 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background-color: #0056b3;
}
ul {
  list-style: none;
  padding: 0;
}
li {
  border: 1px solid #ddd;
  padding: 10px;
  margin: 10px 0;
  border-radius: 4px;
  background-color: #fff;
}
</style>

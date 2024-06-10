<template>
  <div class="license-chooser">
    <h2>数合保</h2>
    <div v-if="currentQuestionIndex < questions.length">
      <progress :value="currentQuestionIndex" :max="questions.length"></progress>
      <h3>维度: {{ questions[currentQuestionIndex].dimension }}</h3>
      <p>{{ questions[currentQuestionIndex].text }}</p>
      <button @click="nextQuestion(true)">是</button>
      <button @click="nextQuestion(false)">否</button>
      <button v-if="questions[currentQuestionIndex].allowNa" @click="nextQuestion(null)">不适用</button>
    </div>
    <div v-else>
      <h3>测评结果</h3>
      <p>总分: {{ totalScore }}/100</p>
      <div v-for="(score, dimension) in dimensionScores" :key="dimension">
        <p>{{ dimension }}: {{ score === 'NA' ? '不适用' : score.toFixed(2) }}</p>
      </div>
      <canvas id="scoreChart"></canvas>
      <button @click="reset">重新测试</button>
      <button @click="saveEvaluation">保存</button>
      <p v-if="saveMessage">{{ saveMessage }}</p>
      <!--<button @click="viewHistory">查看历史测评结果</button>>-->
    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js';
import { nextTick } from 'vue';

// Register Chart.js components
Chart.register(...registerables);

export default {
  data() {
    return {
      currentQuestionIndex: 0,
      totalScore: 0,
      answers: [],
      questions: [],
      dimensionScores: {},
      maxScores: {},
      saveMessage: ''
    };
  },
  mounted() {
    fetch('http://localhost:5000/questions')
      .then(response => response.json())
      .then(data => {
        this.questions = data;
        this.calculateMaxScores();
      })
      .catch(error => {
        console.error('Error fetching questions:', error);
      });
  },
  methods: {
    calculateMaxScores() {
      this.questions.forEach(question => {
        if (!this.maxScores[question.dimension]) {
          this.maxScores[question.dimension] = 0;
        }
        this.maxScores[question.dimension] += Math.max(question.yesScore, question.noScore);
      });
    },
    nextQuestion(answer) {
      const question = this.questions[this.currentQuestionIndex];
      this.answers.push({ ...question, answer });

      if (answer !== null) {
        const score = answer ? question.yesScore : question.noScore;
        if (!this.dimensionScores[question.dimension]) {
          this.dimensionScores[question.dimension] = { total: 0, count: 0, applicable: true };
        }
        this.dimensionScores[question.dimension].total += score;
        this.dimensionScores[question.dimension].count += 1;
      } else {
        if (!this.dimensionScores[question.dimension]) {
          this.dimensionScores[question.dimension] = { total: 0, count: 0, applicable: false };
        } else {
          this.dimensionScores[question.dimension].applicable = false;
        }
      }

      this.currentQuestionIndex++;
      if (this.currentQuestionIndex === this.questions.length) {
        this.calculateScore();
      }
    },
    async calculateScore() {
      let totalScore = 0;
      let applicableDimensions = 0;

      for (const dimension in this.dimensionScores) {
        if (this.dimensionScores[dimension].applicable) {
          const dimensionTotalScore = this.dimensionScores[dimension].total;
          const dimensionMaxScore = this.maxScores[dimension];
          const normalizedScore = (dimensionTotalScore / dimensionMaxScore) * 100;
          this.dimensionScores[dimension] = normalizedScore;
          totalScore += normalizedScore;
          applicableDimensions++;
        } else {
          this.dimensionScores[dimension] = 'NA';
        }
      }

      // 计算总分为所有适用维度的平均值
      this.totalScore = applicableDimensions ? (totalScore / applicableDimensions).toFixed(2) : 'NA';

      await nextTick();
      this.renderChart();
    },
    renderChart() {
      const ctx = document.getElementById('scoreChart').getContext('2d');
      const labels = Object.keys(this.dimensionScores).filter(dimension => this.dimensionScores[dimension] !== 'NA');
      const data = Object.values(this.dimensionScores).filter(score => score !== 'NA');

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
    },
    reset() {
      this.currentQuestionIndex = 0;
      this.answers = [];
      this.dimensionScores = {};
      this.totalScore = 0;
      this.maxScores = {};
      this.calculateMaxScores();
      this.saveMessage = '';
    },
    saveEvaluation() {
      const evaluation = {
        totalScore: this.totalScore,
        dimensionScores: JSON.stringify(this.dimensionScores),
        answers: JSON.stringify(this.answers)
      };

      fetch('http://localhost:5000/save-evaluation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(evaluation)
      })
      .then(response => {
        if (response.ok) {
          return response.json();
        }
        throw new Error('Network response was not ok.');
      })
      .then(() => {
        this.saveMessage = '评估结果保存成功！';
      })
      .catch(error => {
        console.error('Error saving evaluation:', error);
        this.saveMessage = '评估结果保存失败，请重试。';
      });
    },
    viewHistory() {
      this.$router.push('/history');
    }
  }
};
</script>

<style scoped>
.license-chooser {
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
label {
  display: block;
  margin: 10px 0;
}
progress {
  width: 100%;
  height: 20px;
  margin-bottom: 20px;
}
</style>

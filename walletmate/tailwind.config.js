module.exports = {
  content: [
    './templates/**/*.html', // Include all HTML files in templates directory
    './**/templates/**/*.html', // Include nested templates
    './**/templates/login/*.html'
  ],
  theme: {
    extend: {
      colors: {
      'dark-blue-c': '#003366',
      'blue-1-c': '#00509e',
      'blue-2-c': '#007acc',
      'blue-3-c': '#66a3ff',
      'light-blue-c': '#cce0ff',


    },},
  },
  plugins: [],
};


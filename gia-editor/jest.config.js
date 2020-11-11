module.exports = {
  // specifies aliases for imports
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
    '^~/(.*)$': '<rootDir>/$1',
    '^vue$': 'vue/dist/vue.common.js',
    '\\.(sass|scss)$': 'jest-css-modules',
  },
  // specifies extensions of files that will be tested
  moduleFileExtensions: ['js', 'vue', 'json'],
  // specifies a regular extension that will be used to find test files in your project
  testRegex: '(/__tests__/.*|\\.(test|spec))\\.(js)$',
  // specifies that .js files must be transformed using babel-jest, and vue files must be transformed using vue-jest
  transform: {
    '^.+\\.js$': 'babel-jest',
    '.*\\.(vue)$': 'vue-jest',
  },
  transformIgnorePatterns: [
    '<rootDir>/node_modules/(?!vuetify)'
  ],
}
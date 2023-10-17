/** @type {import('next').NextConfig} */

const pkg = require("./package.json");

// starts a command line process to get the git hash
const commitHash = require("child_process")
  .execSync('git log --pretty=format:"%h" -n1')
  .toString()
  .trim();

const nextConfig = {
  output: "export",
  basePath:
    // TODO: Change to load from env variable
    process.env.NODE_ENV === "production" ? "/awesome-fastapi-projects" : "",
  env: {
    commitHash,
    frontendAppVersion: pkg.version,
  },
};

module.exports = nextConfig;

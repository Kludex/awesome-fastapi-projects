/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  basePath:
    process.env.NODE_ENV === "production" ? "/awesome-fastapi-projects" : "",
};
// TODO: Add loading some configs from .env file, revision, etc.

module.exports = nextConfig;

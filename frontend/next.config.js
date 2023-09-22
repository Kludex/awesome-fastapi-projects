/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  basePath:
    process.env.NODE_ENV === "production" ? "/awesome-fastapi-projects" : "",
};

module.exports = nextConfig;

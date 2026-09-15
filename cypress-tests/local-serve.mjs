#!/usr/bin/env node
/**
 * Static file server for local/Cypress use.
 * Rewrites the production <base href> to "/" so CSS/JS resolve locally.
 * Production HTML keeps: <base href="https://webmusic.pages.dev/">
 */
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const HOST = '127.0.0.1'
const PORT = Number(process.env.PORT || 5500)

const PROD_BASE_RE = /<base href="https:\/\/webmusic\.pages\.dev\/"\s*\/?>/g
const LOCAL_BASE = '<base href="/">'

const PRETTY = {
  '/': '/index.html',
  '/apps': '/apps.html',
  '/evaluation': '/evaluation.html',
  '/submit': '/submit.html',
  '/tagsinfo': '/tagsinfo.html',
  '/index': '/index.html',
}

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
  '.pdf': 'application/pdf',
}

function safeResolve(urlPath) {
  const decoded = decodeURIComponent(urlPath.split('?')[0])
  const mapped = PRETTY[decoded] || decoded
  const resolved = path.resolve(ROOT, '.' + mapped)
  if (!resolved.startsWith(ROOT + path.sep) && resolved !== ROOT) {
    return null
  }
  return resolved
}

const server = http.createServer((req, res) => {
  const urlPath = req.url || '/'
  let filePath = safeResolve(urlPath)

  if (!filePath) {
    res.writeHead(403).end('Forbidden')
    return
  }

  if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
    filePath = path.join(filePath, 'index.html')
  }

  if (!fs.existsSync(filePath) || !fs.statSync(filePath).isFile()) {
    res.writeHead(404).end('Not found')
    return
  }

  const ext = path.extname(filePath).toLowerCase()
  const type = MIME[ext] || 'application/octet-stream'

  try {
    let body = fs.readFileSync(filePath)
    if (ext === '.html') {
      const text = body.toString('utf8').replace(PROD_BASE_RE, LOCAL_BASE)
      body = Buffer.from(text, 'utf8')
    }
    res.writeHead(200, { 'Content-Type': type, 'Cache-Control': 'no-store' })
    res.end(body)
  } catch (err) {
    res.writeHead(500).end(String(err))
  }
})

server.listen(PORT, HOST, () => {
  console.log(`Local override server at http://${HOST}:${PORT}`)
  console.log(`Serving ${ROOT} (rewrites production <base> to /)`)
})

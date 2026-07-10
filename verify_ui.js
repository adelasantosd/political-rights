const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  // Serve the dist directory
  const { exec } = require('child_process');
  const server = exec('npx serve 05_webapp/dist -p 3000');

  await new Promise(r => setTimeout(r, 2000)); // Wait for server

  try {
    // Desktop view
    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto('http://localhost:3000');
    await page.waitForSelector('h1');
    await page.screenshot({ path: 'desktop_home.png' });

    // Switch to Costa Rica
    await page.selectOption('select', 'Costa Rica');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'desktop_home_cr.png' });

    // Mobile view
    await page.setViewportSize({ width: 375, height: 812 }); // iPhone X
    await page.goto('http://localhost:3000');
    await page.waitForSelector('h1');
    await page.screenshot({ path: 'mobile_home.png' });

    // Test Gap Map
    await page.click('button:has-text("Anchoring / Gap Map")');
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'mobile_gapmap.png' });

    console.log("Screenshots captured successfully.");
  } catch (e) {
    console.error("Verification failed", e);
  } finally {
    await browser.close();
    server.kill();
    process.exit(0);
  }
})();

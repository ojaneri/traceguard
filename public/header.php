<?php
function renderHeader($title = "TraceGuard", $showLanguageSelector = false, $showDocumentationLink = false) {
    $logoPath = "logo.png";
    $documentationUrl = "../index.html";

    return '
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>' . htmlspecialchars($title) . '</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: system-ui, Segoe UI, Roboto, Arial, sans-serif;
                margin: 0;
                background: #0f172a;
                color: #e5e7eb;
                min-height: 100vh;
            }

            .header {
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 15px 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            }

            .header-content {
                max-width: 1200px;
                margin: 0 auto;
            }

            .header-logo {
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 15px;
            }

            .header-logo img {
                height: 80px;
                width: auto;
                margin-right: 15px;
            }

            .header-logo h1 {
                font-size: 2.5em;
                font-weight: 300;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }

            .header-nav {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 30px;
                margin-top: 15px;
            }

            .language-selector select {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 8px 15px;
                font-size: 14px;
                cursor: pointer;
            }

            .language-selector select option {
                background: #2c3e50;
                color: white;
            }

            .nav-link {
                color: #ffc107;
                text-decoration: none;
                font-weight: 500;
                padding: 8px 16px;
                border-radius: 6px;
                transition: all 0.3s ease;
            }

            .nav-link:hover {
                background: rgba(255, 193, 7, 0.2);
                color: white;
            }

            main {
                max-width: 1200px;
                margin: 30px auto;
                padding: 0 20px;
            }

            .card {
                background: #1f2937;
                padding: 30px;
                border-radius: 15px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            }

            .footer {
                background: linear-gradient(135deg, #2c3e50, #34495e);
                color: white;
                text-align: center;
                padding: 25px;
                border-radius: 15px;
                margin-top: 40px;
            }

            .footer p {
                margin: 0;
                font-size: 1.1em;
                font-weight: bold;
            }

            .footer a {
                color: #ffc107;
                text-decoration: none;
                transition: color 0.3s ease;
            }

            .footer a:hover {
                color: white;
            }

            @media (max-width: 768px) {
                .header-logo {
                    flex-direction: column;
                    gap: 10px;
                }

                .header-logo h1 {
                    font-size: 2em;
                }

                .header-nav {
                    flex-direction: column;
                    gap: 15px;
                }
            }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="header-logo">
                    <img src="' . htmlspecialchars($logoPath) . '" alt="TraceGuard Logo">
                    <h1>TraceGuard</h1>
                </div>
                <div class="header-nav">
                    ' . ($showLanguageSelector ? '
                    <div class="language-selector">
                        <select id="languageSelect" onchange="changeLanguage()">
                            <option value="pt">🇧🇷 Português</option>
                            <option value="en">🇺🇸 English</option>
                        </select>
                    </div>' : '') . '
                    ' . ($showDocumentationLink ? '
                    <a href="' . htmlspecialchars($documentationUrl) . '" class="nav-link">📖 Documentação</a>' : '') . '
                </div>
            </div>
        </div>
        <main>';
}
?>
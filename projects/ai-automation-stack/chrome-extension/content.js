/**
 * AI Chat Scraper Extension - Content Script
 * ===========================================
 * Scrapes and autosaves chat content from lovable.dev, v0.dev, and bolt.new
 * 
 * Features:
 * - Auto-scrapes visible chats every 5 seconds
 * - Saves to localStorage
 * - Hotkey-triggered full export (Ctrl+Shift+E)
 * - Extracts full chat history
 * - JSON export with metadata
 * 
 * Usage:
 * - Install as Chrome/Firefox extension
 * - Press Ctrl+Shift+E to export current chat
 * - Chats are automatically saved to localStorage
 */

(function () {
    'use strict';

    // Configuration
    const CONFIG = {
        SCRAPE_INTERVAL: 5000, // 5 seconds
        STORAGE_KEY: 'ai_chat_exports',
        HOTKEY: 'ctrl+shift+e',
        MAX_CHATS_PER_SITE: 100,
    };

    // Site configurations with selectors
    const SITES = {
        'lovable.dev': {
            name: 'Lovable',
            chatSelector: '[class*="chat"], [class*="conversation"], [class*="message"], main, article',
            userMessageSelector: '[class*="user"], [class*="human"], [data-role="user"]',
            aiMessageSelector: '[class*="assistant"], [class*="ai"], [class*="bot"], [data-role="assistant"]',
            contentSelector: 'p, div, span',
            titleSelector: 'h1, [class*="title"], [class*="header"]',
        },
        'v0.dev': {
            name: 'v0',
            chatSelector: '[class*="chat"], [class*="conversation"], [class*="message"], main, article',
            userMessageSelector: '[class*="user"], [class*="human"], [data-role="user"]',
            aiMessageSelector: '[class*="assistant"], [class*="ai"], [class*="bot"], [data-role="assistant"]',
            contentSelector: 'p, div, span, pre, code',
            titleSelector: 'h1, [class*="title"], [class*="header"]',
        },
        'bolt.new': {
            name: 'Bolt',
            chatSelector: '[class*="chat"], [class*="conversation"], [class*="message"], main, article',
            userMessageSelector: '[class*="user"], [class*="human"], [data-role="user"]',
            aiMessageSelector: '[class*="assistant"], [class*="ai"], [class*="bot"], [data-role="assistant"]',
            contentSelector: 'p, div, span, pre, code',
            titleSelector: 'h1, [class*="title"], [class*="header"]',
        },
    };

    // Current site info
    let currentSite = null;
    let chatData = null;
    let isScraping = false;

    /**
     * Initialize the scraper
     */
    function init() {
        // Detect current site
        const hostname = window.location.hostname.replace('www.', '');
        currentSite = SITES[hostname];

        if (!currentSite) {
            console.log('AI Chat Scraper: Unknown site, running in generic mode');
            currentSite = {
                name: 'Generic',
                chatSelector: 'main, article, body',
                userMessageSelector: '[class*="user"], [class*="human"]',
                aiMessageSelector: '[class*="assistant"], [class*="ai"], [class*="bot"]',
                contentSelector: 'p, div, span',
                titleSelector: 'h1, title',
            };
        }

        console.log(`AI Chat Scraper: Initialized for ${currentSite.name}`);

        // Start auto-scraping
        startAutoScrape();

        // Listen for hotkey
        document.addEventListener('keydown', handleHotkey);

        // Listen for messages from popup/background
        chrome.runtime.onMessage.addListener(handleMessage);
    }

    /**
     * Start automatic scraping
     */
    function startAutoScrape() {
        setInterval(scrapeCurrentChat, CONFIG.SCRAPE_INTERVAL);
        // Initial scrape
        setTimeout(scrapeCurrentChat, 1000);
    }

    /**
     * Handle hotkey press
     */
    function handleHotkey(e) {
        if (e.key.toLowerCase() === 'e' && e.ctrlKey && e.shiftKey) {
            e.preventDefault();
            exportChat();
        }
    }

    /**
     * Handle messages from popup/background script
     */
    function handleMessage(request, sender, sendResponse) {
        if (request.action === 'export') {
            const data = scrapeCurrentChat();
            sendResponse({ success: true, data: data });
        } else if (request.action === 'getStored') {
            const stored = getStoredChats();
            sendResponse({ success: true, data: stored });
        } else if (request.action === 'clear') {
            clearStoredChats();
            sendResponse({ success: true });
        }
        return true;
    }

    /**
     * Scrape current chat
     */
    function scrapeCurrentChat() {
        if (isScraping) {
            console.log('AI Chat Scraper: Already scraping, skipping...');
            return chatData;
        }

        isScraping = true;

        try {
            const title = extractTitle();
            const messages = extractMessages();
            const timestamp = new Date().toISOString();
            const url = window.location.href;

            chatData = {
                id: generateId(),
                site: currentSite.name,
                title: title,
                url: url,
                timestamp: timestamp,
                messageCount: messages.length,
                messages: messages,
                exportedAt: timestamp,
            };

            // Save to localStorage
            saveChat(chatData);

            console.log(`AI Chat Scraper: Scraped ${messages.length} messages from ${currentSite.name}`);

            return chatData;

        } catch (error) {
            console.error('AI Chat Scraper: Error scraping chat:', error);
            return null;
        } finally {
            isScraping = false;
        }
    }

    /**
     * Extract chat title
     */
    function extractTitle() {
        // Try various selectors for title
        const selectors = currentSite.titleSelector.split(',');

        for (const selector of selectors) {
            const element = document.querySelector(selector.trim());
            if (element && element.textContent.trim()) {
                return element.textContent.trim().slice(0, 100);
            }
        }

        // Fallback: use URL or generic title
        const path = window.location.pathname.split('/').filter(Boolean).pop();
        return path || `Chat ${new Date().toLocaleDateString()}`;
    }

    /**
     * Extract messages from chat
     */
    function extractMessages() {
        const messages = [];

        // Find all potential message containers
        const chatContainer = document.querySelector(currentSite.chatSelector);
        if (!chatContainer) {
            console.log('AI Chat Scraper: No chat container found');
            return messages;
        }

        // Get all text content blocks
        const allElements = chatContainer.querySelectorAll('*');

        let currentRole = null;
        let currentContent = [];

        for (const element of allElements) {
            // Skip invisible elements
            if (!isElementVisible(element)) {
                continue;
            }

            const text = element.textContent.trim();
            if (!text || text.length < 5) {
                continue;
            }

            // Detect if this is a user or AI message
            const role = detectMessageRole(element);

            if (role && role !== currentRole) {
                // Save previous message if exists
                if (currentRole && currentContent.length > 0) {
                    messages.push({
                        role: currentRole,
                        content: cleanContent(currentContent.join('\n')),
                        timestamp: extractTimestamp(element),
                    });
                }

                // Start new message
                currentRole = role;
                currentContent = [text];
            } else if (currentRole) {
                // Continue current message
                currentContent.push(text);
            }
        }

        // Don't forget the last message
        if (currentRole && currentContent.length > 0) {
            messages.push({
                role: currentRole,
                content: cleanContent(currentContent.join('\n')),
            });
        }

        return messages;
    }

    /**
     * Detect message role from element
     */
    function detectMessageRole(element) {
        const classList = element.className.toLowerCase();
        const id = element.id.toLowerCase();
        const text = element.textContent.toLowerCase();

        // Check for user indicators
        const userIndicators = ['user', 'human', 'you', 'input', 'prompt'];
        for (const indicator of userIndicators) {
            if (classList.includes(indicator) || id.includes(indicator)) {
                return 'user';
            }
        }

        // Check for AI indicators
        const aiIndicators = ['assistant', 'ai', 'bot', 'gpt', 'cursor', 'response', 'output'];
        for (const indicator of aiIndicators) {
            if (classList.includes(indicator) || id.includes(indicator)) {
                return 'assistant';
            }
        }

        // Check text patterns
        if (text.startsWith('user:') || text.startsWith('human:')) {
            return 'user';
        }
        if (text.startsWith('assistant:') || text.startsWith('ai:') || text.startsWith('bot:')) {
            return 'assistant';
        }

        return null;
    }

    /**
     * Check if element is visible
     */
    function isElementVisible(element) {
        const style = window.getComputedStyle(element);
        if (style.display === 'none' || style.visibility === 'hidden') {
            return false;
        }
        if (element.offsetParent === null) {
            return false;
        }
        return true;
    }

    /**
     * Extract timestamp from element
     */
    function extractTimestamp(element) {
        const timeElement = element.querySelector('time');
        if (timeElement) {
            return timeElement.getAttribute('datetime') || timeElement.textContent;
        }
        return null;
    }

    /**
     * Clean message content
     */
    function cleanContent(content) {
        if (!content) return '';

        // Remove excessive whitespace
        content = content.replace(/\n{3,}/g, '\n\n');
        content = content.trim();

        return content;
    }

    /**
     * Generate unique ID
     */
    function generateId() {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    }

    /**
     * Save chat to localStorage
     */
    function saveChat(chat) {
        try {
            const stored = getStoredChats();

            // Check for duplicates
            const exists = stored.some(c =>
                c.url === chat.url &&
                c.messageCount === chat.messageCount &&
                Math.abs(new Date(c.timestamp) - new Date(chat.timestamp)) < 60000
            );

            if (exists) {
                console.log('AI Chat Scraper: Chat already stored, skipping...');
                return;
            }

            // Add to beginning
            stored.unshift(chat);

            // Limit stored chats
            const trimmed = stored.slice(0, CONFIG.MAX_CHATS_PER_SITE);

            localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(trimmed));
            console.log(`AI Chat Scraper: Saved chat (${trimmed.length} total)`);

        } catch (error) {
            console.error('AI Chat Scraper: Error saving chat:', error);
        }
    }

    /**
     * Get stored chats from localStorage
     */
    function getStoredChats() {
        try {
            const stored = localStorage.getItem(CONFIG.STORAGE_KEY);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('AI Chat Scraper: Error reading stored chats:', error);
            return [];
        }
    }

    /**
     * Clear stored chats
     */
    function clearStoredChats() {
        localStorage.removeItem(CONFIG.STORAGE_KEY);
        console.log('AI Chat Scraper: Stored chats cleared');
    }

    /**
     * Export chat as JSON
     */
    function exportChat() {
        const data = scrapeCurrentChat();

        if (!data) {
            alert('No chat data to export');
            return;
        }

        const json = JSON.stringify(data, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentSite.name}_chat_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('AI Chat Scraper: Chat exported');
    }

    /**
     * Format chat as Markdown
     */
    function formatAsMarkdown(chat) {
        let md = `# ${chat.title}\n\n`;
        md += `*Source: ${chat.site}*\n`;
        md += `*Exported: ${chat.exportedAt}*\n\n`;
        md += `---\n\n`;

        for (const message of chat.messages) {
            const role = message.role === 'user' ? '👤 User' : '🤖 Assistant';
            md += `## ${role}\n\n`;
            md += `${message.content}\n\n`;
            md += `---\n\n`;
        }

        return md;
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();

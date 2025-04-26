/**
 * Quote Manager for BanditGUI
 *
 * This script handles loading and displaying geek pop culture quotes.
 */

class QuoteManager {
    constructor() {
        this.quotes = [];
        this.welcomeQuotes = [];
        this.currentQuoteIndex = 0;
    }

    /**
     * Initialize the quote manager
     */
    async init() {
        try {
            // Load welcome quotes
            await this.loadWelcomeQuotes();

            // Start quote rotation for status messages
            this.startQuoteRotation();
        } catch (error) {
            console.error('Error initializing quote manager:', error);
        }
    }

    /**
     * Load welcome quotes for terminal
     */
    async loadWelcomeQuotes(count = 1) {
        try {
            const response = await fetch(`/quotes/welcome?count=${count}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.welcomeQuotes = data.quotes;
                return this.welcomeQuotes;
            } else {
                console.error('Error loading welcome quotes:', data.message);
                return this.getDefaultWelcomeQuotes();
            }
        } catch (error) {
            console.error('Error fetching welcome quotes:', error);
            return this.getDefaultWelcomeQuotes();
        }
    }

    /**
     * Get default welcome quotes if API fails
     */
    getDefaultWelcomeQuotes() {
        return [
            '"Have you tried turning it off and on again?"'
        ];
    }

    /**
     * Get a random quote
     */
    async getRandomQuote() {
        try {
            const response = await fetch('/quotes/random');
            const data = await response.json();

            if (data.status === 'success') {
                return data.quote;
            } else {
                console.error('Error loading random quote:', data.message);
                return this.getDefaultQuote();
            }
        } catch (error) {
            console.error('Error fetching random quote:', error);
            return this.getDefaultQuote();
        }
    }

    /**
     * Get a default quote if API fails
     */
    getDefaultQuote() {
        return {
            text: "The code must flow.",
            source: "Dune (modified)",
            character: "Paul Atreides as a programmer"
        };
    }

    /**
     * Format a quote object into a string
     */
    formatQuote(quote) {
        return `"${quote.text}"`;
    }

    /**
     * Get welcome quotes for terminal
     */
    getWelcomeQuotes() {
        return this.welcomeQuotes.length > 0 ? this.welcomeQuotes : this.getDefaultWelcomeQuotes();
    }

    /**
     * Start quote rotation for status messages
     */
    startQuoteRotation(intervalMs = 60000) {
        // Update quote every minute
        setInterval(async () => {
            const statusMessage = document.getElementById('quote-message');
            if (statusMessage) {
                const quote = await this.getRandomQuote();
                statusMessage.innerHTML = this.formatQuote(quote);
                statusMessage.classList.add('quote-fade-in');

                // Remove animation class after animation completes
                setTimeout(() => {
                    statusMessage.classList.remove('quote-fade-in');
                }, 2000);
            }
        }, intervalMs);
    }
}

// Initialize Quote Manager when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.quoteManager = new QuoteManager();
    window.quoteManager.init();
});

/**
 * Jobbee Analytics Utility
 */
const Analytics = {
    trackEvent: function(eventName, eventParams = {}) {
        if (typeof gtag === 'function') {
            gtag('event', eventName, eventParams);
        } else {
            console.warn('GA4 is not initialized. Event missed:', eventName);
        }
    },

    // Specific Reusable Events
    trackJobSearch: function(keyword, location) {
        this.trackEvent('search', {
            search_term: keyword,
            location_term: location
        });
    },

    trackJobClick: function(jobTitle, employerName) {
        this.trackEvent('select_content', {
            content_type: 'job_posting',
            item_id: jobTitle,
            employer: employerName
        });
    },

    trackAccountSignup: function(method) {
        this.trackEvent('sign_up', {
            method: method
        });
    }
};

// Consent management
function grantAnalyticsConsent() {
    if (typeof gtag === 'function') {
        gtag('consent', 'update', {
            'ad_storage': 'granted',
            'analytics_storage': 'granted'
        });
    }
    localStorage.setItem('cookie_consent', 'true');
}

// Auto-check consent on load
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('cookie_consent') === 'true') {
        grantAnalyticsConsent();
    }
});

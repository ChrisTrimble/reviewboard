/*
 * A list of key bindings for the page.
 */
var gActions = [
    { // Previous file
        keys: "aAKP<m",
        onPress: function() {
            scrollToAnchor(GetNextAnchor(BACKWARD, ANCHOR_FILE));
        },
    	description: "Previous file"
    },

    { // Next file
        keys: "fFJN>",
        onPress: function() {
            scrollToAnchor(GetNextAnchor(FORWARD, ANCHOR_FILE));
        },
    	description: "Next file"
    },

    { // Previous diff
        keys: "sSkp,",
        onPress: function() {
            scrollToAnchor(GetNextAnchor(BACKWARD, ANCHOR_CHUNK | ANCHOR_FILE));
        },
    	description: "Previous diff"
    },

    { // Next diff
        keys: "dDjn.",
        onPress: function() {
            scrollToAnchor(GetNextAnchor(FORWARD, ANCHOR_CHUNK | ANCHOR_FILE));
        },
    	description: "Next diff"
    },

    { // Recenter
        keys: unescape("0D%"),
        onPress: function() { scrollToAnchor(gAnchors[gSelectedAnchor]); },
    	description: "Recenter"
    },

    { // Previous comment
        keys: "[x",
        onPress: function() {
            scrollToAnchor(GetNextAnchor(BACKWARD, ANCHOR_COMMENT));
        },
    	description: "Previous comment"
    },

    { // Next comment
        keys: "]c",
        onPress: function() {
            scrollToAnchor(GetNextAnchor(FORWARD, ANCHOR_COMMENT));
        },
    	description: "Next comment"
    },

    { // Go to header
        keys: "gu;",
        onPress: function() {},
    	description: "Go to header"
    },

    { // Go to footer
        keys: "GU:",
        onPress: function() {},
    	description: "Go to footer"
    },

    { // Go to footer
        keys: "?",
        onPress: function() {
    		displayHelpScreen();
    	},
    	description: "Show Help"
    }
];
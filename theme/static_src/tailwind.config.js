/**
 * This is a minimal config.
 *
 * If you need the full config, get it from here:
 * https://unpkg.com/browse/tailwindcss@latest/stubs/defaultConfig.stub.js
 */
const defaultColors = require('tailwindcss/colors')

module.exports = {
    /**
     * Stylesheet generation mode.
     *
     * Set mode to "jit" if you want to generate your styles on-demand as you author your templates;
     * Set mode to "aot" if you want to generate the stylesheet in advance and purge later (aka legacy mode).
     */
    mode: "jit",

    purge: [
        /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

        /*  Templates within theme app (<tailwind_app_name>/templates), e.g. base.html. */
        '../templates/**/*.html',

        /* 
         * Main templates directory of the project (BASE_DIR/templates).
         * Adjust the following line to match your project structure.
         */
        '../../templates/**/*.html',
        
        /* 
         * Templates in other django apps (BASE_DIR/<any_app_name>/templates).
         * Adjust the following line to match your project structure.
         */
        '../../**/templates/**/*.html',

        /**
         * JS: If you use Tailwind CSS in JavaScript, uncomment the following lines and make sure
         * patterns match your project structure.
         */
        /* JS 1: Ignore any JavaScript in node_modules folder. */
        // '!../../**/node_modules',
        /* JS 2: Process all JavaScript files in the project. */
        // '../../**/*.js',

        /**
         * Python: If you use Tailwind CSS classes in Python, uncomment the following line
         * and make sure the pattern below matches your project structure.
         */
        // '../../**/*.py'
    ],
    darkMode: false, // or 'media' or 'class'
    theme: {
      extend: {
      fontFamily: {
        'paris': ['Paris2024','-apple-system', 'BlinkMacSystemFont', 'system-ui', 'sans-serif'],
      },
      
      colors: {
        ...defaultColors,
        // Base
        'base': '#2C2C2C',
        
        // Primary (Blue) Scale
        primary: {
          10: '#F3F8FF',
          20: '#E0EAFF',
          30: '#C2D6FF',
          40: '#7FA8FF',
          50: '#4A7FE0',
          60: '#11309F',
          70: '#0D2580',
          80: '#091B60',
          90: '#051240',
        },
        
        // Green Scale
        green: {
          10: '#F5FFF8',
          20: '#E0FFF0',
          30: '#B8FFD9',
          40: '#7FFFB8',
          50: '#4CF9BA',
          60: '#09714B',
          70: '#075A3C',
          80: '#05442D',
          90: '#032D1E',
        },
      },
      
      // Custom gradient utilities
      backgroundImage: {
        'gradient-green-light': 'linear-gradient(90.27deg, #4CF9BA 0.27%, #20BF86 104.59%)',
        'gradient-green-dark': 'linear-gradient(90.27deg, #3CCC98 0.27%, #1C9A6D 104.59%)',
        'gradient-blue-light': 'linear-gradient(90.27deg, #4BB8F4 0.27%, #3666E0 104.59%)',
        'gradient-blue-dark': 'linear-gradient(90.27deg, #3C98CC 0.27%, #1C3F9A 104.59%)',
      },
      
      fontSize: {
        'h1': ['3rem', { lineHeight: '3.5rem', fontWeight: '800', letterSpacing: '-0.02em' }],      // 48px
        'h2': ['2.25rem', { lineHeight: '2.75rem', fontWeight: '700', letterSpacing: '-0.01em' }],  // 36px
        'h3': ['1.875rem', { lineHeight: '2.375rem', fontWeight: '600' }],                          // 30px
        'h4': ['1.5rem', { lineHeight: '2rem', fontWeight: '600' }],                                // 24px
      },
    },
    },
    variants: {
        extend: {},
    },
    plugins: [
        /**
         * '@tailwindcss/forms' is the forms plugin that provides a minimal styling
         * for forms. If you don't like it or have own styling for forms,
         * comment the line below to disable '@tailwindcss/forms'.
         */
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/line-clamp'),
        require('@tailwindcss/aspect-ratio'),
    ],
}

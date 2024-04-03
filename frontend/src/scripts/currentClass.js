function findCurrentClasses(courses, inputDay, inputTime) {
    // Helper function to convert time strings to date objects for comparison
    const timeToDate = (time) => {
        // Assuming time is in the format "HH:MM AM/PM"
        let [hour, minute] = time.split(':');
        const period = minute.substring(3); // Get AM/PM
        minute = minute.slice(0, -3); // Remove AM/PM from minutes

        if (period === 'PM' && +hour !== 12) {
            hour = +hour + 12; // Convert hour to 24-hour format if PM
        } else if (period === 'AM' && +hour === 12) {
            hour = 0; // Convert 12 AM to 00 hours
        }

        const date = new Date();
        date.setHours(+hour, +minute, 0, 0); // Reset seconds and milliseconds
        
        return date;
    };

    // Helper function to check if the course matches the input day and time
    const isCourseAtTime = (courseDay, courseTimes, inputDay, inputTime) => {
        if (!courseDay.includes(inputDay)) return false;
        if (courseTimes === "TBA") return false; // Skip courses with TBA times
        if (courseTimes === "By Arrangement") return false; // Skip online courses (assuming no specific meeting times
        const [startTimeStr, endTimeStr] = courseTimes.split(' - ');
        const startTime = timeToDate(startTimeStr);
        const endTime = timeToDate(endTimeStr);
        const inputDateTime = timeToDate(inputTime); // Append ":00" to match the expected format

        return inputDateTime >= startTime && inputDateTime <= endTime;
    };

    // Main filtering function
    const currentClasses = courses.filter(course => {
        // Check the primary meeting time
        if (isCourseAtTime(course.Meetday, course.Times, inputDay, inputTime)) {
            return true;
        }

        // Check additional sessions if any
        if (course.Additional_Sessions) {
            return course.Additional_Sessions.some(session =>
                isCourseAtTime(session.Additional_Meetday, session.Additional_Times, inputDay, inputTime)
            );
        }

        return false;
    });

    // Print or use the filtered courses as needed
    console.log("Current classes at the given time:");
    currentClasses.forEach(course => {
        console.log(`Class name: ${course.Title}\nProfessor: ${course.Professor}\nTime: ${course.Times}\nLocation: ${course.Location}`);
    });

    // Optionally, return the filtered list of classes
    return currentClasses;
}

// Open a json file of courses and pass it to the function
const courses = require('../data/courses.json');

findCurrentClasses(courses, "M", "7:00 PM");

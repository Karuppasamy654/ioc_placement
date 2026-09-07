import datetime
from backend.models.schemas import Roadmap

class ICSExporter:
    @staticmethod
    def generate_ics_content(roadmap: Roadmap, candidate_name: str = "Student", start_date: datetime.date = None) -> str:
        """
        Generates standard iCalendar (.ics) format string mapping roadmap days to consecutive dates.
        """
        if start_date is None:
            start_date = datetime.date.today()

        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//AI Placement Preparation Agent//EN",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            f"X-WR-CALNAME:{candidate_name} Placement Prep Schedule"
        ]

        now_stamp = datetime.datetime.now().strftime("%Y%M%DT%H%M%SZ")

        for day in roadmap.days:
            event_date = start_date + datetime.timedelta(days=(day.day_number - 1))
            dt_start = event_date.strftime("%Y%m%D").replace("-", "")
            
            # Summary & Description
            summary = f"Placement Prep - Day {day.day_number}: {day.day_title}"
            
            tasks_desc = []
            for t in day.tasks:
                tasks_desc.append(f"- {t.topic} ({t.duration_hours} hrs, Priority: {t.priority}): {t.practice_task}")
            
            description = f"Overview: {roadmap.overview}\\n\\nDaily Tasks:\\n" + "\\n".join(tasks_desc)
            
            lines.extend([
                "BEGIN:VEVENT",
                f"UID:placement-prep-day{day.day_number}-{dt_start}@ai-placement-agent",
                f"DTSTAMP:{now_stamp}",
                f"DTSTART;VALUE=DATE:{dt_start}",
                f"SUMMARY:{summary}",
                f"DESCRIPTION:{description}",
                "STATUS:CONFIRMED",
                "END:VEVENT"
            ])

        lines.append("END:VCALENDAR")
        return "\r\n".join(lines)

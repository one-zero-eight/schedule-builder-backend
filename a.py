import asyncio

from src.parsers.electives.parser import ElectiveCoursesParser


if __name__ == "__main__":
    parser = ElectiveCoursesParser()
    asyncio.run(
        parser.get_all_timeslots(
            "1uSGLyKSAXq1q7vxMVKWi3qE86uydQgPhFNO8TV9omZM"
        )
    )

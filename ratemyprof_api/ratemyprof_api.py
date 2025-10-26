import requests
import json
import csv

SCHOOL_ID = "U2Nob29sLTg4Mg=="

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/115.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Referer": "https://www.ratemyprofessors.com/",
}

def get_professor_info(first_name, last_name):
    url = "https://www.ratemyprofessors.com/graphql"
    query = """
    query TeacherSearchPaginationQuery($count: Int!, $cursor: String, $query: TeacherSearchQuery!) {
      search: newSearch {
        teachers(query: $query, first: $count, after: $cursor) {
          edges {
            node {
              firstName
              lastName
              id
              department
              avgRating
              avgDifficulty
              numRatings
              wouldTakeAgainPercent
              school { name }
            }
          }
        }
      }
    }
    """
    variables = {
        "count": 10,
        "cursor": None,
        "query": {"text": f"{first_name} {last_name}", "schoolID": SCHOOL_ID, "fallback": True}
    }

    response = requests.post(url, headers=HEADERS, json={"query": query, "variables": variables}, timeout=10)
    if response.status_code != 200:
        print("Error: Status code", response.status_code)
        return None

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error: Response is not JSON")
        return None

    teachers = data.get("data", {}).get("search", {}).get("teachers", {}).get("edges", [])
    for t in teachers:
        node = t.get("node", {})
        if node.get("firstName", "").strip().lower() == first_name.strip().lower() and \
           node.get("lastName", "").strip().lower() == last_name.strip().lower():
            return node
    return None

def get_professor_comments(professor_id, count=50):
    url = "https://www.ratemyprofessors.com/graphql"
    query = """
    query RatingsListQuery($count: Int!, $id: ID!, $courseFilter: String, $cursor: String) {
      node(id: $id) {
        __typename
        ... on Teacher {
          ratings(first: $count, after: $cursor, courseFilter: $courseFilter) {
            edges {
              node {
                comment
                ratingTags
                class
                date
              }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
        }
      }
    }
    """
    variables = {"count": count, "id": professor_id, "courseFilter": None, "cursor": None}

    response = requests.post(url, headers=HEADERS, json={"query": query, "variables": variables}, timeout=10)
    if response.status_code != 200:
        print("Error fetching comments:", response.status_code)
        return []

    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Comments response not JSON")
        return []

    edges = data.get("data", {}).get("node", {}).get("ratings", {}).get("edges", [])
    comments = []
    for e in edges:
        n = e.get("node", {})
        comments.append({
            "comment": n.get("comment", ""),
            "tags": n.get("ratingTags", ""),
            "class": n.get("class", ""),
            "date": n.get("date", "")
        })
    return comments

def save_combined_json(professor, comments, filename):
    combined = {
        "professor_info": {
            "firstName": professor.get("firstName"),
            "lastName": professor.get("lastName"),
            "department": professor.get("department"),
            "school": professor.get("school", {}).get("name"),
            "avgRating": professor.get("avgRating"),
            "avgDifficulty": professor.get("avgDifficulty"),
            "numRatings": professor.get("numRatings"),
            "wouldTakeAgainPercent": professor.get("wouldTakeAgainPercent")
        },
        "comments": comments
    }
    with open(filename, "w") as f:
        json.dump(combined, f, indent=4)
    print(f"Saved JSON: {filename}")

def save_combined_csv(professor, comments, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)

        # Write professor info section
        writer.writerow(["Professor Information"])
        writer.writerow(["First Name", professor.get("firstName")])
        writer.writerow(["Last Name", professor.get("lastName")])
        writer.writerow(["Department", professor.get("department")])
        writer.writerow(["School", professor.get("school", {}).get("name")])
        writer.writerow(["Average Rating", professor.get("avgRating")])
        writer.writerow(["Average Difficulty", professor.get("avgDifficulty")])
        writer.writerow(["Number of Ratings", professor.get("numRatings")])
        writer.writerow(["Would Take Again (%)", professor.get("wouldTakeAgainPercent")])
        writer.writerow([])

        # Write comments section
        writer.writerow(["Comments"])
        writer.writerow(["Date", "Class", "Tags", "Comment"])
        for c in comments:
            writer.writerow([c.get("date"), c.get("class"), ", ".join(c.get("tags", [])), c.get("comment")])

    print(f"Saved CSV: {filename}")

def main():
    print("Rate My Professors SCU - Live Data")
    first_name = input("Enter professor's first name: ").strip()
    last_name = input("Enter professor's last name: ").strip()

    professor = get_professor_info(first_name, last_name)
    if not professor:
        print("Professor not found or unable to fetch info.")
        return

    comments = get_professor_comments(professor.get("id"))

    filename_base = f"{first_name}_{last_name}"
    save_combined_json(professor, comments, f"{filename_base}.json")
    save_combined_csv(professor, comments, f"{filename_base}.csv")

if __name__ == "__main__":
    main()

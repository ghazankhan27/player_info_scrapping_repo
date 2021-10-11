from bs4 import BeautifulSoup
import requests

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem


def get_random_user_agent():
    software_names = [SoftwareName.CHROME.value, SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value]
    user_agent_rotator = UserAgent(
        software_names=software_names, operating_systems=operating_systems, limit=100
    )
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


def get_data():

    # Variables
    player_data = []
    player_data_QB = []
    player_data_RB = []
    player_data_WR_TE = []
    accepted_positions = ["QB", "RB", "WR", "TE"]
    max_experience_years = 3

    # Setting base url and headers for the request
    baseurl = "https://www.pro-football-reference.com"
    headers = {"User-Agent": get_random_user_agent()}

    # Getting the html of the page
    r = requests.get(baseurl + "/years/2021/fantasy.htm", headers=headers)
    soup = BeautifulSoup(r.content, "lxml")
    soup.prettify()

    # List out all the players in the players table
    player_table = soup.find("table", id="fantasy")
    player_table_body = player_table.find("tbody")
    player_table_body_rows = player_table_body.find_all("tr")

    # Go through each player to get the data required
    for row in player_table_body_rows:

        # Check if row contains player data
        is_head = row.get("class")
        if is_head != None:
            continue

        # Get the link to the players page
        player_stat_page = row.find("td", class_="left")
        player_stat_page_link = player_stat_page.find("a")
        player_stat_page_link_text = str(player_stat_page_link.get("href"))

        # Get the player name
        player_name = player_stat_page_link.text

        # Get the player age
        player_age_columns = row.find_all("td")
        for column in player_age_columns:
            col_name = column.get("data-stat")
            if col_name == "age":
                player_age = column.text
                break

        # Get a random user agent and send requests to get data for each of the player
        headers = {"User-Agent": get_random_user_agent()}
        player_data_page = requests.get(
            baseurl + player_stat_page_link_text, headers=headers
        )

        # Getting the html of the player data page
        player_data_soup = BeautifulSoup(player_data_page.content, "lxml")
        player_data_soup.prettify()

        # Get the player data from meta data area i.e Team name and Position
        player_data_meta = player_data_soup.find("div", id="meta")
        player_data_meta_data = player_data_meta.find_all("p")
        for meta_data in player_data_meta_data:
            try:
                data = str(meta_data.text)
                if "Position" in data:
                    player_position = data.split()
                    player_position = player_position[1]
                    continue
                if "Team" in data:
                    player_team = data.replace("Team: ", "")
                    break
            except:
                continue

        # If player's position is accepted
        if player_position in accepted_positions:

            player_season_stat_table = None

            # Get the season stats table
            if player_position == "QB":
                player_season_stat_table = player_data_soup.find("table", id="passing")

            elif player_position == "RB":
                player_season_stat_table = player_data_soup.find(
                    "table", id="rushing_and_receiving"
                )

            else:
                player_season_stat_table = player_data_soup.find(
                    "table", id="receiving_and_rushing"
                )

            # If season stats table exists
            if player_season_stat_table != None:

                # Data storage places
                recent_game_stats = []
                season_stats = []

                # Finding recent game table and all the data objects from it
                recent_game_stats_table = player_data_soup.find("table", id="stats")
                recent_game_stats_table_body = recent_game_stats_table.find("tbody")
                recent_game_stats_table_body_rows = (
                    recent_game_stats_table_body.find_all("tr")
                )

                # Get the latest game from the recent games stats table
                recent_game_stats_required_row = None
                for row in recent_game_stats_table_body_rows:
                    if row.get("id") != None:
                        recent_game_stats_required_row = row
                    else:
                        break

                # Get all data objects from the latest game
                player_recent_stats_table_columns = (
                    recent_game_stats_required_row.find_all("td")
                )

                # Finding the season stats table and getting all data objects from it
                player_season_stat_table_body = player_season_stat_table.find("tbody")
                player_season_stat_table_body_rows = (
                    player_season_stat_table_body.find_all("tr")
                )
                player_season_stat_table_body_latest_row = (
                    player_season_stat_table_body_rows[-1]
                )
                player_season_stat_table_body_columns = (
                    player_season_stat_table_body_latest_row.find_all("td")
                )

                # Calculating player experience
                player_years_experience = len(player_season_stat_table_body_rows)

                # If player has over 3 years of experience, discard him
                if player_years_experience > max_experience_years:
                    continue

                else:

                    # Player data is valid and should be scrapped, position : QB
                    if player_position == "QB":

                        # Scrapping season stats
                        for column in player_season_stat_table_body_columns:
                            column_name = column.get("data-stat")

                            if column_name == "pass_cmp_perc":
                                player_pass_cmp_perc = str(column.text)
                                season_stats.append(player_pass_cmp_perc)
                                continue
                            if column_name == "pass_yds":
                                player_pass_yds = str(column.text)
                                season_stats.append(player_pass_yds)
                                continue
                            if column_name == "pass_td":
                                player_pass_td = str(column.text)
                                season_stats.append(player_pass_td)
                                continue
                            if column_name == "pass_int":
                                player_pass_int = str(column.text)
                                season_stats.append(player_pass_int)
                                continue
                            if column_name == "pass_rating":
                                player_pass_rating = str(column.text)
                                season_stats.append(player_pass_rating)
                                break

                        # Scrapping recent game stats
                        for column in player_recent_stats_table_columns:
                            column_name = column.get("data-stat")

                            if column_name == "pass_cmp":
                                player_pass_cmp = str(column.text)
                                recent_game_stats.append(player_pass_cmp)
                                continue
                            if column_name == "pass_att":
                                player_pass_att = str(column.text)
                                recent_game_stats.append(player_pass_att)
                                continue
                            if column_name == "pass_yds":
                                player_pass_yds = str(column.text)
                                recent_game_stats.append(player_pass_yds)
                                continue
                            if column_name == "pass_td":
                                player_pass_td = str(column.text)
                                recent_game_stats.append(player_pass_td)
                                continue
                            if column_name == "pass_int":
                                player_pass_int = str(column.text)
                                recent_game_stats.append(player_pass_int)
                                continue
                            if column_name == "pass_rating":
                                player_pass_rating = str(column.text)
                                recent_game_stats.append(player_pass_rating)
                                continue
                            if column_name == "pass_rating":
                                player_pass_rating = str(column.text)
                                recent_game_stats.append(player_pass_rating)
                                continue
                            if column_name == "rush_att":
                                player_rush_att = str(column.text)
                                recent_game_stats.append(player_rush_att)
                                continue
                            if column_name == "rush_yds":
                                player_rush_yds = str(column.text)
                                recent_game_stats.append(player_rush_yds)
                                continue
                            if column_name == "rush_td":
                                player_rush_td = str(column.text)
                                recent_game_stats.append(player_rush_td)
                                break

                        # Creating the object for the player
                        player_data_obj = {
                            "name": player_name,
                            "age": player_age,
                            "team": player_team,
                            "position": player_position,
                            "recent_stats": recent_game_stats,
                            "season_stats": season_stats,
                        }
                        print(player_data_obj)
                        player_data.append(player_data_obj)

                    # Scrape data for position:RB
                    elif player_position == "RB":

                        # Scrapping season stats
                        for column in player_season_stat_table_body_columns:
                            column_name = column.get("data-stat")

                            if column_name == "rush_yds":
                                player_rush_yds = str(column.text)
                                season_stats.append(player_rush_yds)
                                continue
                            if column_name == "rush_yds_per_att":
                                player_rush_yds_per_att = str(column.text)
                                season_stats.append(player_rush_yds_per_att)
                                continue
                            if column_name == "targets":
                                player_targets = str(column.text)
                                season_stats.append(player_targets)
                                continue
                            if column_name == "rec":
                                player_rec = str(column.text)
                                season_stats.append(player_rec)
                                continue
                            if column_name == "rec_yds":
                                player_rec_yds = str(column.text)
                                season_stats.append(player_rec_yds)
                                continue
                            if column_name == "rec_td":
                                player_rec_td = str(column.text)
                                season_stats.append(player_rec_td)
                                break

                        # Scrapping recent game stats
                        for column in player_recent_stats_table_columns:
                            column_name = column.get("data-stat")

                            if column_name == "rush_att":
                                player_rush_att = str(column.text)
                                recent_game_stats.append(player_rush_att)
                                continue
                            if column_name == "rush_yds":
                                player_rush_yds = str(column.text)
                                recent_game_stats.append(player_rush_yds)
                                continue
                            if column_name == "rush_yds_per_att":
                                player_rush_yds_per_att = str(column.text)
                                recent_game_stats.append(player_rush_yds_per_att)
                                continue
                            if column_name == "rush_td":
                                player_rush_td = str(column.text)
                                recent_game_stats.append(player_rush_td)
                                continue
                            if column_name == "targets":
                                player_targets = str(column.text)
                                recent_game_stats.append(player_targets)
                                continue
                            if column_name == "rec":
                                player_rec = str(column.text)
                                recent_game_stats.append(player_rec)
                                continue
                            if column_name == "rec_yds":
                                player_rec_yds = str(column.text)
                                recent_game_stats.append(player_rec_yds)
                                continue
                            if column_name == "rush_att":
                                player_rush_att = str(column.text)
                                recent_game_stats.append(player_rush_att)
                                continue
                            if column_name == "rec_td":
                                player_rec_td = str(column.text)
                                recent_game_stats.append(player_rec_td)
                                continue
                            if column_name == "off_pct":
                                player_off_pct = str(column.text)
                                recent_game_stats.append(player_off_pct)
                                break

                        # Creating the object for the player
                        player_data_obj = {
                            "name": player_name,
                            "age": player_age,
                            "team": player_team,
                            "position": player_position,
                            "recent_stats": recent_game_stats,
                            "season_stats": season_stats,
                        }

                        player_data.append(player_data_obj)
                        print(player_data_obj)

                    # Scrape data for position: TE or WR
                    else:

                        # Scrapping season stats
                        for column in player_season_stat_table_body_columns:
                            column_name = column.get("data-stat")

                            if column_name == "targets":
                                player_targets = str(column.text)
                                season_stats.append(player_targets)
                                continue
                            if column_name == "rec":
                                player_rec = str(column.text)
                                season_stats.append(player_rec)
                                continue
                            if column_name == "rec_yds":
                                player_rec_yds = str(column.text)
                                season_stats.append(player_rec_yds)
                                continue
                            if column_name == "rec_td":
                                player_rec_td = str(column.text)
                                season_stats.append(player_rec_td)
                                break

                        # Scrapping recent game stats
                        for column in player_recent_stats_table_columns:
                            column_name = column.get("data-stat")

                            if column_name == "targets":
                                player_targets = str(column.text)
                                recent_game_stats.append(player_targets)
                                continue
                            if column_name == "rec":
                                player_rec = str(column.text)
                                recent_game_stats.append(player_rec)
                                continue
                            if column_name == "rec_yds":
                                player_rec_yds = str(column.text)
                                recent_game_stats.append(player_rec_yds)
                                continue
                            if column_name == "rush_td":
                                player_rush_td = str(column.text)
                                recent_game_stats.append(player_rush_td)
                                continue
                            if column_name == "off_pct":
                                player_off_pct = str(column.text)
                                recent_game_stats.append(player_off_pct)
                                break

                        # Creating the object for the player
                        player_data_obj = {
                            "name": player_name,
                            "age": player_age,
                            "team": player_team,
                            "position": player_position,
                            "recent_stats": recent_game_stats,
                            "season_stats": season_stats,
                        }

                        player_data.append(player_data_obj)

                        print(player_data_obj)
            else:
                continue
        else:
            continue


get_data()

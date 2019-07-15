import os
import time
import requests
from bs4 import BeautifulSoup
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()


def main():
	URL_PAPERS = "http://www.cs.toronto.edu/~hinton/papers.html"
	URL_ROOT = "http://www.cs.toronto.edu/~hinton/"
	response = requests.get(URL_PAPERS)
	if(response.status_code == 200):
		print("Correctly loaded website\nParsing the source code...")
		src = response.text
		soup = BeautifulSoup(src, "lxml")
		print("Finished!")

		print("Extracting papers...\n")
		papers = []
		raw_papers = soup.find('table').find_all('tr')

		for row in raw_papers:
			year = row.td.text
			if row.select('td')[1].b != None:
				title = row.select('td')[1].b.text
				title = " ".join(title.split())
			else:
				title = "title_missing"

			authors = row.contents[2].contents[0]
			authors = " ".join(authors.split())
			if row.find('a', href=True) != None:
				current_paper_url = row.find('a', href=True).attrs['href']
			else:
				current_paper_url = "missing"

			papers.append([str(year), str(authors), str(title), str(current_paper_url)])
		print("Finished extracting articles from the website!")
		print("It's time to clean them up a little bit (replace whitespaces, remove special chars)")

		for paper in papers:
			paper[0] = " ".join(paper[0].split())
			for r in (("\n", ""), ("\r", ""), (" ", "_"), (",",""), (".","")):
				paper[1] = paper[1].replace(*r)
				paper[2] = paper[2].replace(*r)

		print("Done!\n")
		print("Extracted " + str(len(papers)) + " papers, they're stored in the \'papers\' array.")

		print("Creating chronological folders to store these papers...")
		root_path = 'hinton/'
		years = set([paper[0] for paper in papers])
		for year in years:
			os.makedirs(root_path + year, exist_ok=True)
		print("Folders created!")
		printProgressBar(0, len(papers), prefix = 'Downloading:', suffix = 'Complete', length = 50)
		for i, paper in enumerate(papers):
			printProgressBar(i + 1, len(papers), prefix = 'Downloading:', suffix = 'Complete', length = 50)
			download_url = ""
			if(("http" in paper[3] and  "pdf" not in paper[3]) or paper[3] == 'missing'):
				print("Can't download - ", paper, "\n")
			elif ("http" in paper[3] and "pdf" in paper[3]):
				download_url = paper[3]
			else:
				download_url = URL_ROOT + paper[3]
				save_path = root_path + paper[0] +"/"+ paper[1] + "-" + paper[2] + ".pdf"
				file = requests.get(download_url)
				if(file.status_code == 200):
					with open(save_path, "wb") as output:
						output.write(file.content)
				else:
					print("File does not exist!")
		
if __name__ == '__main__':
	main()
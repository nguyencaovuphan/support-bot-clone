import os
import glob
from scraper import OptiSignsScraper
from assistant import OptiBotAssistant

def main():
    print("--- BẮT ĐẦU CHẠY DAILY JOB ---")
    
    scraper = OptiSignsScraper()
    scraper.save_all()
    
    assistant = OptiBotAssistant()
    
    md_files = glob.glob(os.path.join(scraper.output_dir, "*.md"))
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for file_path in md_files:
        status = assistant.index_file(file_path)
        if status == "added":
            added_count += 1
        elif status == "updated":
            updated_count += 1
        elif status == "skipped":
            skipped_count += 1
            
    assistant.save_db()
    
    print("\n--- BÁO CÁO ĐỒNG BỘ VECTOR STORE ---")
    print(f"Tổng số file xử lý: {len(md_files)}")
    print(f"Added (Mới): {added_count}")
    print(f"Updated (Cập nhật): {updated_count}")
    print(f"Skipped (Không đổi): {skipped_count}")
    print(f"Tổng số Chunks hiện tại trong Vector Store: {len(assistant.db['chunks'])}")
    
    print("\n--- RUNNING SANITY CHECK ---")
    test_query = "How do I add a YouTube video?"
    print(f"Question: '{test_query}'\n")
    answer = assistant.ask_optibot(test_query)
    print("OptiBot Answer:")
    print(answer)
    print("---------------------------------")
    
    with open("last_run_artifact.log", "w", encoding="utf-8") as log_file:
        log_file.write(f"Status: Success\nAdded: {added_count}\nUpdated: {updated_count}\nSkipped: {skipped_count}")

if __name__ == "__main__":
    main()
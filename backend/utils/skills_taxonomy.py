import json
import re
from pathlib import Path

class SkillTaxonomy:
    def __init__(self):
        # Load skills taxonomy
        taxonomy_path = Path('backend/utils/data/skills_taxonomy.json')
        with open(taxonomy_path, 'r') as f:
            self.taxonomy = json.load(f)
            
        # Create a flattened skills list with aliases
        self.skills_list = [] # List of all skill names
        self.skills_to_category = {} # Maps skill name to (category, subcategory)
        self.skill_aliases = {} # Maps alias to skill name
        
        for category, subcategories in self.taxonomy.items():
            for subcategory, skills in subcategories.items():
                for skill in skills:
                    # Each skill can be a dict with name and aliases
                    if isinstance(skill, dict):
                        skill_name = skill['name']
                        aliases = skill.get('aliases', [])
                        
                        self.skills_list.append(skill_name.lower())
                        self.skills_to_category[skill_name.lower()] = (category, subcategory)
                        
                        for alias in aliases:
                            self.skills_list.append(alias.lower())
                            self.skills_to_category[alias.lower()] = (category, subcategory)
                            self.skill_aliases[alias.lower()] = skill_name.lower()
                    else:
                        self.skills_list.append(skill.lower())
                        self.skills_to_category[skill.lower()] = (category, subcategory)
        
        # Sort by length (longest first) to prioritize longer skill names
        self.skills_list = sorted(self.skills_list, key=len, reverse=True)
    
    def extract_skills(self, text):
        """Extract skills from text using the taxonomy"""
        text = text.lower()
        found_skills = set()
        
        # Look for exact matches
        for skill in self.skills_list:
            # Use word boundary for exact matching
            if re.search(r'\b' + re.escape(skill) + r'\b', text):
                # If it's an alias, use the primary skill name
                canonical_skill = self.skill_aliases.get(skill, skill)
                found_skills.add(canonical_skill)
        
        return list(found_skills)
    
    def get_skill_vector(self, skills):
        """Create a binary vector of all skills in the taxonomy"""
        # Create a set of unique, canonical skill names
        canonical_skills = set()
        for skill in skills:
            canonical_skill = self.skill_aliases.get(skill.lower(), skill.lower())
            canonical_skills.add(canonical_skill)
        
        # Create binary vector using only primary skill names (not aliases)
        primary_skills = set(s for s in self.skills_list if s not in self.skill_aliases)
        vector = [1 if skill in canonical_skills else 0 for skill in primary_skills]
        return vector

# Example usage
if __name__ == "__main__":
    taxonomy = SkillTaxonomy()
    text = "I have 5 years of experience with Python and Django. I also have experience with AWS and Docker."
    skills = taxonomy.extract_skills(text)
    print(taxonomy.skill_aliases)